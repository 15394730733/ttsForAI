"""History service.

Manages TTS generation history records.
"""

import json
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logger import get_logger
from src.models.history import History
from src.models.task import Task, TaskStatus

# Get logger with context
log = get_logger("HistoryService")


class HistoryService:
    """Service for managing TTS generation history."""

    def __init__(self, max_size: int = None):
        """Initialize history service.

        Args:
            max_size: Maximum number of history records (default: from settings)
        """
        self.max_size = max_size or settings.MAX_HISTORY_SIZE

    async def create_history(
        self,
        task: Task,
        db: AsyncSession,
    ) -> History | None:
        """Create history record from completed task.

        Args:
            task: Completed task
            db: Database session

        Returns:
            Created history record or None if task not completed
        """
        if task.status != TaskStatus.COMPLETED or not task.file_path:
            log.warning(f"Cannot create history for incomplete task {task.task_id}")
            return None

        try:
            # Create text summary (first 100 chars)
            text_summary = (
                task.text[:100] + "..." if len(task.text) > 100 else task.text
            )

            # Create voice params JSON
            voice_params = json.dumps(
                {
                    "voice_name": task.voice_name,
                    "rate": task.rate,
                    "pitch": task.pitch,
                    "volume": task.volume,
                },
                ensure_ascii=False,
            )

            # Get file size
            file_path = Path(task.file_path)
            file_size = file_path.stat().st_size if file_path.exists() else 0

            log.debug(
                f"Creating history record: task_id={task.task_id}, "
                f"file_size={file_size}, text_summary_length={len(text_summary)}"
            )

            # Create history record
            history = History(
                task_id=task.task_id,
                text_summary=text_summary,
                voice_params=voice_params,
                file_path=task.file_path,
                file_size=file_size,
                status="active",
            )

            db.add(history)

            # Auto-cleanup old records
            await self._cleanup_old_records(db)

            await db.commit()
            await db.refresh(history)

            log.info(
                f"History operation: CREATE - id={history.id}, task_id={task.task_id}"
            )
            return history

        except Exception:
            log.exception(f"History operation: CREATE_FAILED - task_id={task.task_id}")
            await db.rollback()
            return None

    async def get_history_list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[History]:
        """Get list of history records.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of history records
        """
        result = await db.execute(
            select(History)
            .order_by(History.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_history_by_id(
        self,
        history_id: int,
        db: AsyncSession,
    ) -> History | None:
        """Get history record by ID.

        Args:
            history_id: History record ID
            db: Database session

        Returns:
            History record or None
        """
        result = await db.execute(select(History).where(History.id == history_id))
        return result.scalar_one_or_none()

    async def get_history_by_task_id(
        self,
        task_id: str,
        db: AsyncSession,
    ) -> History | None:
        """Get history record by task ID.

        Args:
            task_id: Task identifier
            db: Database session

        Returns:
            History record or None
        """
        result = await db.execute(select(History).where(History.task_id == task_id))
        return result.scalar_one_or_none()

    async def delete_history(
        self,
        history_id: int,
        db: AsyncSession,
        delete_file: bool = False,
    ) -> bool:
        """Delete history record.

        Args:
            history_id: History record ID
            db: Database session
            delete_file: Whether to also delete the audio file

        Returns:
            True if deleted successfully
        """
        try:
            history = await self.get_history_by_id(history_id, db)
            if not history:
                return False

            # Delete file if requested
            if delete_file and history.file_path:
                file_path = Path(history.file_path)
                if file_path.exists():
                    try:
                        file_path.unlink()
                        log.debug(f"Deleted audio file: {file_path}")
                    except Exception as e:
                        log.warning(f"Failed to delete audio file: {e}")

            # Delete record
            await db.execute(delete(History).where(History.id == history_id))
            await db.commit()

            log.info(
                f"History operation: DELETE - id={history_id}, task_id={history.task_id}"
            )
            return True

        except Exception:
            log.exception(f"History operation: DELETE_FAILED - id={history_id}")
            await db.rollback()
            return False

    async def clear_all_history(
        self,
        db: AsyncSession,
        delete_files: bool = False,
    ) -> int:
        """Clear all history records.

        Args:
            db: Database session
            delete_files: Whether to also delete audio files

        Returns:
            Number of records deleted
        """
        try:
            # Get all records
            records = await self.get_history_list(db, limit=1000)
            count = len(records)

            log.info(
                f"History operation: CLEAR_ALL - count={count}, delete_files={delete_files}"
            )

            # Delete files if requested
            if delete_files:
                deleted_files = 0
                for record in records:
                    if record.file_path:
                        file_path = Path(record.file_path)
                        if file_path.exists():
                            try:
                                file_path.unlink()
                                deleted_files += 1
                            except Exception as e:
                                log.warning(f"Failed to delete file {file_path}: {e}")

                log.debug(f"Deleted {deleted_files}/{count} audio files")

            # Delete all records
            await db.execute(delete(History))
            await db.commit()

            log.info(f"History operation: CLEAR_COMPLETE - deleted_count={count}")
            return count

        except Exception:
            log.exception("History operation: CLEAR_ALL_FAILED")
            await db.rollback()
            return 0

    async def get_history_count(self, db: AsyncSession) -> int:
        """Get total number of history records.

        Args:
            db: Database session

        Returns:
            Number of records
        """
        result = await db.execute(select(func.count(History.id)))
        return result.scalar() or 0

    async def _cleanup_old_records(self, db: AsyncSession) -> None:
        """Remove oldest records if exceeding max_size.

        Args:
            db: Database session
        """
        count = await self.get_history_count(db)
        if count <= self.max_size:
            return

        # Calculate how many to remove
        to_remove = count - self.max_size

        # Get oldest records
        result = await db.execute(
            select(History).order_by(History.created_at.asc()).limit(to_remove)
        )
        old_records = result.scalars().all()

        # Delete them
        for record in old_records:
            await db.execute(delete(History).where(History.id == record.id))

        log.info(f"Auto-cleaned {to_remove} old history records")


# Global history service instance
history_service = HistoryService()
