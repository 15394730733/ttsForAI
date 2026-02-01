"""Unit tests for Queue service.

Tests task queue management functionality.
"""
import pytest
import asyncio

from src.models.task import Task, TaskStatus
from src.services.queue_service import QueueService


class TestQueueService:
    """Test Queue service."""

    def test_init(self):
        """Test QueueService initialization."""
        service = QueueService(max_size=5)

        assert service.max_size == 5
        assert service.queue.empty()
        assert service.current_task is None
        assert service.is_processing is False

    @pytest.mark.asyncio
    async def test_enqueue_task(self):
        """Test enqueuing a task."""
        service = QueueService(max_size=5)

        task = Task(
            task_id="test-001",
            text="Test task",
        )

        success = await service.enqueue(task)

        assert success is True
        assert service.get_queue_size() == 1
        assert task.status == TaskStatus.QUEUED

    @pytest.mark.asyncio
    async def test_enqueue_multiple_tasks(self):
        """Test enqueuing multiple tasks."""
        service = QueueService(max_size=5)

        for i in range(3):
            task = Task(
                task_id=f"test-{i}",
                text=f"Task {i}",
            )
            await service.enqueue(task)

        assert service.get_queue_size() == 3

    @pytest.mark.asyncio
    async def test_enqueue_full_queue(self):
        """Test enqueuing to a full queue."""
        service = QueueService(max_size=2)

        # Fill queue
        for i in range(2):
            task = Task(task_id=f"test-{i}", text="Task")
            await service.enqueue(task)

        # Try to add to full queue
        task = Task(task_id="test-overflow", text="Overflow")
        success = await service.enqueue(task)

        assert success is False
        assert service.is_full()

    @pytest.mark.asyncio
    async def test_dequeue_task(self):
        """Test dequeuing a task."""
        service = QueueService(max_size=5)

        task = Task(task_id="test-001", text="Test")
        await service.enqueue(task)

        dequeued = await service.dequeue()

        assert dequeued is not None
        assert dequeued.task_id == "test-001"
        assert service.is_empty()

    @pytest.mark.asyncio
    async def test_dequeue_empty_queue(self):
        """Test dequeuing from empty queue."""
        service = QueueService(max_size=5)

        dequeued = await service.dequeue()

        assert dequeued is None

    def test_get_queue_size(self):
        """Test getting queue size."""
        service = QueueService()

        # Empty queue
        assert service.get_queue_size() == 0

    def test_is_empty(self):
        """Test checking if queue is empty."""
        service = QueueService()

        assert service.is_empty() is True

    def test_is_full(self):
        """Test checking if queue is full."""
        service = QueueService(max_size=1)
        assert service.is_full() is False

    def test_get_status(self):
        """Test getting queue status."""
        service = QueueService(max_size=10)

        status = service.get_status()

        assert isinstance(status, dict)
        assert "queued_count" in status
        assert "processing_count" in status
        assert "max_queue_size" in status
        assert status["max_queue_size"] == 10
        assert status["queued_count"] == 0

    @pytest.mark.asyncio
    async def test_increment_completed(self):
        """Test incrementing completed counter."""
        service = QueueService()

        service.increment_completed()
        service.increment_completed()

        status = service.get_status()
        assert status["completed_count"] == 2

    @pytest.mark.asyncio
    async def test_increment_failed(self):
        """Test incrementing failed counter."""
        service = QueueService()

        service.increment_failed()
        service.increment_failed()

        status = service.get_status()
        assert status["failed_count"] == 2

    @pytest.mark.asyncio
    async def test_set_current_task(self):
        """Test setting current task."""
        service = QueueService()

        task = Task(task_id="test-001", text="Current")
        service.set_current_task(task)

        assert service.current_task is not None
        assert service.current_task.task_id == "test-001"
        assert service.is_processing is True

        # Clear
        service.set_current_task(None)

        assert service.current_task is None
        assert service.is_processing is False

    @pytest.mark.asyncio
    async def test_clear_queue(self):
        """Test clearing queue."""
        service = QueueService(max_size=5)

        # Add tasks
        for i in range(3):
            task = Task(task_id=f"test-{i}", text="Task")
            await service.enqueue(task)

        # Clear
        count = await service.clear_queue()

        assert count == 3
        assert service.is_empty()
