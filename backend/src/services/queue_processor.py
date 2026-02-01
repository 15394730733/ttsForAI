"""Background queue processor.

Continuously processes tasks from the queue.
"""

import asyncio

from src.core.database import AsyncSessionLocal
from src.core.logger import logger
from src.models.task import Task, TaskStatus
from src.services.history_service import history_service
from src.services.queue_service import queue_service
from src.services.tts_service import TTSService


class QueueProcessor:
    """Background task queue processor."""

    def __init__(self):
        """Initialize queue processor."""
        self.is_running = False
        self._task: asyncio.Task | None = None
        self.tts_service = TTSService()

    async def start(self):
        """Start the background processor."""
        if self.is_running:
            logger.warning("Queue processor is already running")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._process_loop())
        logger.info("Queue processor started")

    async def stop(self):
        """Stop the background processor."""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Queue processor stopped")

    async def _process_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                # Get next task from queue
                task = await queue_service.dequeue()

                if task is None:
                    # No tasks, wait a bit
                    await asyncio.sleep(0.5)
                    continue

                # Process the task
                await self._process_task(task)

            except Exception as e:
                logger.error(f"Error in process loop: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _process_task(self, task: Task):
        """Process a single task.

        Args:
            task: Task to process
        """
        async with AsyncSessionLocal() as db:
            try:
                logger.info(f"Processing task {task.task_id}")

                # Refresh task from database
                from sqlalchemy import select

                result = await db.execute(
                    select(Task).where(Task.task_id == task.task_id)
                )
                task = result.scalar_one_or_none()

                if not task:
                    logger.error(f"Task {task.task_id} not found in database")
                    return

                if task.status != TaskStatus.QUEUED:
                    logger.warning(
                        f"Task {task.task_id} is not queued (status: {task.status})"
                    )
                    return

                # Set as current task
                queue_service.set_current_task(task)
                task.status = TaskStatus.PROCESSING
                task.started_at = task.started_at or task.__class__.started_at.default
                await db.commit()

                # Generate audio
                logger.info(f"Starting TTS generation for task {task.task_id}")
                await self.tts_service.generate_audio(task)
                logger.info(f"TTS generation completed for task {task.task_id}")

                # Save to database
                await db.commit()
                logger.info(f"Task {task.task_id} saved to database")

                # Create history record if completed successfully
                if task.status == TaskStatus.COMPLETED:
                    await history_service.create_history(task, db)
                    queue_service.increment_completed()
                    logger.info(f"History record created for task {task.task_id}")
                else:
                    queue_service.increment_failed()
                    logger.warning(f"Task {task.task_id} failed to complete")

                # Clear current task
                queue_service.set_current_task(None)
                logger.info(f"Task {task.task_id} processing complete")

            except Exception as e:
                logger.error(
                    f"Task processing failed for {task.task_id}: {e}", exc_info=True
                )
                queue_service.set_current_task(None)
                queue_service.increment_failed()

                # Update task status
                if task:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(e)
                    try:
                        await db.commit()
                    except Exception:
                        await db.rollback()


# Global queue processor instance
queue_processor = QueueProcessor()
