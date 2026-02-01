"""Task queue service.

Manages TTS task queue with async processing.
"""

import asyncio
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logger import logger
from src.models.task import Task, TaskStatus


class QueueService:
    """Service for managing TTS task queue."""

    def __init__(self, max_size: int = None):
        """Initialize queue service.

        Args:
            max_size: Maximum queue size (default: from settings)
        """
        self.max_size = max_size or settings.MAX_QUEUE_SIZE
        self.queue: asyncio.Queue[Task] = asyncio.Queue(maxsize=self.max_size)
        self.current_task: Task | None = None
        self.is_processing = False
        self._completed_count = 0
        self._failed_count = 0

    async def enqueue(self, task: Task) -> bool:
        """Add task to queue.

        Args:
            task: Task to add

        Returns:
            True if task was queued successfully

        Raises:
            asyncio.QueueFull: If queue is full
        """
        if self.queue.full():
            logger.warning(f"Queue is full ({self.max_size} tasks)")
            return False

        await self.queue.put(task)
        task.status = TaskStatus.QUEUED
        logger.info(f"Task {task.task_id} added to queue (size: {self.queue.qsize()})")
        return True

    async def dequeue(self) -> Task | None:
        """Get next task from queue.

        Returns:
            Next task or None if queue is empty
        """
        if self.queue.empty():
            return None

        try:
            task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            logger.info(f"Task {task.task_id} removed from queue")
            return task
        except TimeoutError:
            return None

    def get_queue_size(self) -> int:
        """Get current queue size.

        Returns:
            Number of tasks in queue
        """
        return self.queue.qsize()

    def is_empty(self) -> bool:
        """Check if queue is empty.

        Returns:
            True if queue is empty
        """
        return self.queue.empty()

    def is_full(self) -> bool:
        """Check if queue is full.

        Returns:
            True if queue is full
        """
        return self.queue.full()

    def get_status(self) -> dict[str, Any]:
        """Get queue status.

        Returns:
            Dictionary with queue status information
        """
        return {
            "queued_count": self.queue.qsize(),
            "processing_count": 1 if self.current_task else 0,
            "completed_count": self._completed_count,
            "failed_count": self._failed_count,
            "max_queue_size": self.max_size,
            "current_task": self.current_task.task_id if self.current_task else None,
        }

    async def get_task_by_id(self, task_id: str, db: AsyncSession) -> Task | None:
        """Get task by ID from database.

        Args:
            task_id: Task identifier
            db: Database session

        Returns:
            Task object or None if not found
        """
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        return result.scalar_one_or_none()

    async def cancel_task(self, task_id: str, db: AsyncSession) -> bool:
        """Cancel a queued task.

        Args:
            task_id: Task identifier
            db: Database session

        Returns:
            True if task was cancelled
        """
        task = await self.get_task_by_id(task_id, db)
        if not task:
            return False

        # Only queued tasks can be cancelled
        if task.status != TaskStatus.QUEUED:
            logger.warning(f"Cannot cancel task {task_id} with status {task.status}")
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        await db.commit()

        # Remove from queue if present
        temp_list = []
        found = False
        while not self.queue.empty():
            t = await self.queue.get()
            if t.task_id == task_id:
                found = True
                break
            temp_list.append(t)

        # Put back other tasks
        for t in temp_list:
            await self.queue.put(t)

        if found:
            logger.info(f"Cancelled task {task_id}")
            return True

        return False

    async def clear_queue(self) -> int:
        """Clear all tasks from queue.

        Returns:
            Number of tasks cleared
        """
        count = 0
        while not self.queue.empty():
            await self.queue.get()
            count += 1

        logger.info(f"Cleared {count} tasks from queue")
        return count

    def set_current_task(self, task: Task | None) -> None:
        """Set current processing task.

        Args:
            task: Task being processed (None when done)
        """
        self.current_task = task
        self.is_processing = task is not None

    def increment_completed(self) -> None:
        """Increment completed task counter."""
        self._completed_count += 1

    def increment_failed(self) -> None:
        """Increment failed task counter."""
        self._failed_count += 1


# Global queue instance
queue_service = QueueService()
