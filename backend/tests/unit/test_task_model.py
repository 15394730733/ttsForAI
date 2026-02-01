"""Unit tests for Task model.

Tests Task model functionality including creation, validation, and methods.
"""
import pytest
from datetime import datetime
from sqlalchemy import select

from src.models.task import Task, TaskStatus


class TestTaskModel:
    """Test Task ORM model."""

    @pytest.mark.asyncio
    async def test_create_task(self, test_db):
        """Test creating a new task."""
        task = Task(
            task_id="test-001",
            text="Hello, world!",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        assert task.task_id == "test-001"
        assert task.text == "Hello, world!"
        assert task.voice_name == "zh-CN-XiaoxiaoNeural"
        assert task.status == TaskStatus.QUEUED
        assert task.progress == 0
        assert task.file_path is None
        assert task.error_message is None
        assert task.created_at is not None

    @pytest.mark.asyncio
    async def test_task_defaults(self, test_db):
        """Test task default values."""
        task = Task(
            task_id="test-002",
            text="Test",
        )

        test_db.add(task)
        await test_db.commit()

        assert task.voice_name == "zh-CN-XiaoxiaoNeural"  # Default
        assert task.rate == 1.0  # Default
        assert task.pitch == 1.0  # Default
        assert task.volume == 1.0  # Default
        assert task.status == TaskStatus.QUEUED
        assert task.progress == 0

    @pytest.mark.asyncio
    async def test_task_status_transitions(self, test_db):
        """Test task status transitions."""
        task = Task(
            task_id="test-003",
            text="Status test",
        )

        test_db.add(task)
        await test_db.commit()

        # queued -> processing
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.now()
        await test_db.commit()

        assert task.status == TaskStatus.PROCESSING
        assert task.started_at is not None

        # processing -> completed
        task.status = TaskStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.now()
        task.file_path = "/output/test-003.mp3"
        await test_db.commit()

        assert task.status == TaskStatus.COMPLETED
        assert task.progress == 100
        assert task.completed_at is not None
        assert task.file_path == "/output/test-003.mp3"

    @pytest.mark.asyncio
    async def test_task_failed_status(self, test_db):
        """Test task failed status."""
        task = Task(
            task_id="test-004",
            text="Failed test",
        )

        test_db.add(task)
        await test_db.commit()

        task.status = TaskStatus.FAILED
        task.error_message = "Network error"
        task.completed_at = datetime.now()
        await test_db.commit()

        assert task.status == TaskStatus.FAILED
        assert task.error_message == "Network error"
        assert task.completed_at is not None

    @pytest.mark.asyncio
    async def test_task_cancelled_status(self, test_db):
        """Test task cancelled status."""
        task = Task(
            task_id="test-005",
            text="Cancelled test",
        )

        test_db.add(task)
        await test_db.commit()

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        await test_db.commit()

        assert task.status == TaskStatus.CANCELLED
        assert task.completed_at is not None

    @pytest.mark.asyncio
    async def test_task_to_dict(self, test_db):
        """Test Task.to_dict() method."""
        task = Task(
            task_id="test-006",
            text="Dict test",
            rate=1.5,
            pitch=0.8,
        )

        test_db.add(task)
        await test_db.commit()

        task_dict = task.to_dict()

        assert isinstance(task_dict, dict)
        assert task_dict["task_id"] == "test-006"
        assert task_dict["text"] == "Dict test"
        assert task_dict["rate"] == 1.5
        assert task_dict["pitch"] == 0.8
        assert task_dict["status"] == TaskStatus.QUEUED
        assert "created_at" in task_dict

    @pytest.mark.asyncio
    async def test_task_repr(self, test_db):
        """Test Task.__repr__() method."""
        task = Task(
            task_id="test-007",
            text="This is a very long text that should be truncated in repr",
        )

        test_db.add(task)
        await test_db.commit()

        repr_str = repr(task)
        assert "test-007" in repr_str
        assert "Task" in repr_str

    @pytest.mark.asyncio
    async def test_query_task_by_id(self, test_db):
        """Test querying task by ID."""
        task = Task(
            task_id="test-008",
            text="Query test",
        )

        test_db.add(task)
        await test_db.commit()

        # Query
        result = await test_db.execute(
            select(Task).where(Task.task_id == "test-008")
        )
        found_task = result.scalar_one_or_none()

        assert found_task is not None
        assert found_task.task_id == "test-008"
        assert found_task.text == "Query test"

    @pytest.mark.asyncio
    async def test_query_tasks_by_status(self, test_db):
        """Test querying tasks by status."""
        # Create multiple tasks
        for i in range(3):
            task = Task(
                task_id=f"test-009-{i}",
                text=f"Task {i}",
                status=TaskStatus.QUEUED if i < 2 else TaskStatus.COMPLETED,
            )
            test_db.add(task)

        await test_db.commit()

        # Query queued tasks
        result = await test_db.execute(
            select(Task).where(Task.status == TaskStatus.QUEUED)
        )
        queued_tasks = result.scalars().all()

        assert len(queued_tasks) == 2

        # Query completed tasks
        result = await test_db.execute(
            select(Task).where(Task.status == TaskStatus.COMPLETED)
        )
        completed_tasks = result.scalars().all()

        assert len(completed_tasks) == 1
