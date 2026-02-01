"""Queue management integration tests.

Tests for queue management functionality including FIFO ordering,
task cancellation, and queue full handling.
"""

import pytest

from src.models.task import Task, TaskStatus
from src.services.queue_service import QueueService


@pytest.mark.asyncio
class TestQueueManagement:
    """Test queue management features."""

    async def test_fifo_ordering(self, test_db):
        """Test that queue maintains FIFO order."""
        service = QueueService(max_size=10)

        # Create tasks in order
        task1 = Task(
            task_id="task1",
            text="First",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task2 = Task(
            task_id="task2",
            text="Second",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task3 = Task(
            task_id="task3",
            text="Third",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        # Enqueue in order
        await service.enqueue(task1)
        await service.enqueue(task2)
        await service.enqueue(task3)

        # Verify FIFO order
        dequeued1 = await service.dequeue()
        assert dequeued1.task_id == "task1"

        dequeued2 = await service.dequeue()
        assert dequeued2.task_id == "task2"

        dequeued3 = await service.dequeue()
        assert dequeued3.task_id == "task3"

    async def test_task_cancel_from_queue(self, test_db):
        """Test cancelling a task that's still in queue."""
        service = QueueService(max_size=10)

        task = Task(
            task_id="cancel_task",
            text="To be cancelled",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        await service.enqueue(task)
        assert service.get_queue_size() == 1

        # Cancel by marking as cancelled
        task.status = TaskStatus.CANCELLED
        await service.dequeue()

        assert task.status == TaskStatus.CANCELLED
        assert service.is_empty()

    async def test_queue_full_handling(self, test_db):
        """Test behavior when queue is full."""
        service = QueueService(max_size=3)

        # Fill queue to max
        for i in range(3):
            task = Task(
                task_id=f"task{i}",
                text=f"Task {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            success = await service.enqueue(task)
            assert success is True

        # Try to add one more - should fail
        extra_task = Task(
            task_id="extra",
            text="Extra task",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        success = await service.enqueue(extra_task)
        assert success is False

        assert service.is_full()
        assert service.get_queue_size() == 3

    async def test_queue_status_tracking(self, test_db):
        """Test that queue status is tracked correctly."""
        service = QueueService(max_size=5)

        # Initial state
        status = service.get_status()
        assert status["queued_count"] == 0
        assert status["processing_count"] == 0
        assert status["completed_count"] == 0

        # Add tasks
        for i in range(3):
            task = Task(
                task_id=f"task{i}",
                text=f"Task {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            await service.enqueue(task)

        status = service.get_status()
        assert status["queued_count"] == 3

        # Process one
        task = await service.dequeue()
        service.set_current_task(task)

        status = service.get_status()
        assert status["queued_count"] == 2
        assert status["processing_count"] == 1

        # Complete one
        service.increment_completed()
        service.set_current_task(None)

        status = service.get_status()
        assert status["queued_count"] == 2
        assert status["processing_count"] == 0
        assert status["completed_count"] == 1

    async def test_clear_queue(self, test_db):
        """Test clearing the queue."""
        service = QueueService(max_size=10)

        # Add tasks
        for i in range(5):
            task = Task(
                task_id=f"task{i}",
                text=f"Task {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            await service.enqueue(task)

        assert service.get_queue_size() == 5

        # Clear queue
        await service.clear_queue()

        assert service.is_empty()
        assert service.get_queue_size() == 0

        # Verify stats are reset
        status = service.get_status()
        assert status["queued_count"] == 0
        assert status["processing_count"] == 0
        assert status["completed_count"] == 0

    async def test_failed_task_tracking(self, test_db):
        """Test tracking of failed tasks."""
        service = QueueService(max_size=10)

        task = Task(
            task_id="fail_task",
            text="Will fail",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        await service.enqueue(task)
        dequeued = await service.dequeue()
        service.set_current_task(dequeued)

        # Mark as failed
        dequeued.status = TaskStatus.FAILED
        service.increment_failed()
        service.set_current_task(None)

        status = service.get_status()
        assert status["processing_count"] == 0
        assert dequeued.status == TaskStatus.FAILED
