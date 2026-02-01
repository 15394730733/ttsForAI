"""Unit tests for History service.

Tests history record management functionality.
"""
import pytest
from datetime import datetime
from sqlalchemy import select

from src.models.task import Task, TaskStatus
from src.models.history import History
from src.services.history_service import HistoryService


class TestHistoryService:
    """Test History service."""

    def test_init(self):
        """Test HistoryService initialization."""
        service = HistoryService(max_size=20)

        assert service.max_size == 20

    @pytest.mark.asyncio
    async def test_create_history_from_completed_task(self, test_db, tmp_path):
        """Test creating history from completed task."""
        service = HistoryService(max_size=20)

        # Create completed task with file
        task = Task(
            task_id="test-001",
            text="This is a test text for history",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
            status=TaskStatus.COMPLETED,
            progress=100,
            file_path=str(tmp_path / "test-001.mp3"),
        )

        # Create audio file
        (tmp_path / "test-001.mp3").write_bytes(b"audio data")

        # Create history
        history = await service.create_history(task, test_db)

        assert history is not None
        assert history.task_id == "test-001"
        assert history.file_path == task.file_path
        assert history.file_size == len(b"audio data")  # Should match actual file size
        assert "This is a test text for history" in history.text_summary or \
               len(history.text_summary) <= 100

    @pytest.mark.asyncio
    async def test_create_history_from_incomplete_task(self, test_db):
        """Test that incomplete tasks don't create history."""
        service = HistoryService(max_size=20)

        # Create incomplete task
        task = Task(
            task_id="test-002",
            text="Incomplete",
            status=TaskStatus.QUEUED,
        )

        history = await service.create_history(task, test_db)

        assert history is None

    @pytest.mark.asyncio
    async def test_create_history_text_summary(self, test_db, tmp_path):
        """Test text summary creation."""
        service = HistoryService(max_size=20)

        # Create task with long text
        long_text = "A" * 200
        task = Task(
            task_id="test-003",
            text=long_text,
            status=TaskStatus.COMPLETED,
            file_path=str(tmp_path / "test-003.mp3"),
        )

        (tmp_path / "test-003.mp3").write_bytes(b"x")

        history = await service.create_history(task, test_db)

        # Summary should be truncated
        assert len(history.text_summary) <= 105  # 100 + "..."

    @pytest.mark.asyncio
    async def test_get_history_list(self, test_db, tmp_path):
        """Test getting history list."""
        service = HistoryService(max_size=20)

        # Create multiple history records
        for i in range(3):
            task = Task(
                task_id=f"test-{i}",
                text=f"Task {i}",
                status=TaskStatus.COMPLETED,
                file_path=str(tmp_path / f"test-{i}.mp3"),
            )
            (tmp_path / f"test-{i}.mp3").write_bytes(b"x")
            await service.create_history(task, test_db)

        # Get list
        histories = await service.get_history_list(test_db)

        assert len(histories) == 3
        assert all(isinstance(h, History) for h in histories)

    @pytest.mark.asyncio
    async def test_get_history_list_with_pagination(self, test_db, tmp_path):
        """Test history list pagination."""
        service = HistoryService(max_size=20)

        # Create 5 records
        for i in range(5):
            task = Task(
                task_id=f"test-{i:03d}",
                text=f"Task {i}",
                status=TaskStatus.COMPLETED,
                file_path=str(tmp_path / f"test-{i}.mp3"),
            )
            (tmp_path / f"test-{i}.mp3").write_bytes(b"x")
            await service.create_history(task, test_db)

        # Get with limit
        histories = await service.get_history_list(test_db, skip=0, limit=3)

        assert len(histories) == 3

        # Get next page
        histories = await service.get_history_list(test_db, skip=3, limit=3)

        assert len(histories) == 2

    @pytest.mark.asyncio
    async def test_get_history_by_id(self, test_db, tmp_path):
        """Test getting history by ID."""
        service = HistoryService(max_size=20)

        task = Task(
            task_id="test-010",
            text="Test",
            status=TaskStatus.COMPLETED,
            file_path=str(tmp_path / "test-010.mp3"),
        )
        (tmp_path / "test-010.mp3").write_bytes(b"x")
        history = await service.create_history(task, test_db)

        # Get by ID
        found = await service.get_history_by_id(history.id, test_db)

        assert found is not None
        assert found.id == history.id
        assert found.task_id == "test-010"

    @pytest.mark.asyncio
    async def test_get_history_by_task_id(self, test_db, tmp_path):
        """Test getting history by task ID."""
        service = HistoryService(max_size=20)

        task = Task(
            task_id="test-011",
            text="Test",
            status=TaskStatus.COMPLETED,
            file_path=str(tmp_path / "test-011.mp3"),
        )
        (tmp_path / "test-011.mp3").write_bytes(b"x")
        await service.create_history(task, test_db)

        # Get by task ID
        found = await service.get_history_by_task_id("test-011", test_db)

        assert found is not None
        assert found.task_id == "test-011"

    @pytest.mark.asyncio
    async def test_delete_history(self, test_db, tmp_path):
        """Test deleting history record."""
        service = HistoryService(max_size=20)

        task = Task(
            task_id="test-012",
            text="Test",
            status=TaskStatus.COMPLETED,
            file_path=str(tmp_path / "test-012.mp3"),
        )
        (tmp_path / "test-012.mp3").write_bytes(b"x")
        history = await service.create_history(task, test_db)

        # Delete
        success = await service.delete_history(history.id, test_db)

        assert success is True

        # Verify deleted
        result = await test_db.execute(
            select(History).where(History.id == history.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_history_with_file(self, test_db, tmp_path):
        """Test deleting history with audio file."""
        service = HistoryService(max_size=20)

        task = Task(
            task_id="test-013",
            text="Test",
            status=TaskStatus.COMPLETED,
            file_path=str(tmp_path / "test-013.mp3"),
        )
        (tmp_path / "test-013.mp3").write_bytes(b"audio data")
        await service.create_history(task, test_db)

        # Delete with file
        success = await service.delete_history(1, test_db, delete_file=True)

        assert success is True
        assert not (tmp_path / "test-013.mp3").exists()

    @pytest.mark.asyncio
    async def test_get_history_count(self, test_db, tmp_path):
        """Test getting history count."""
        service = HistoryService(max_size=20)

        # Initially 0
        count = await service.get_history_count(test_db)
        assert count == 0

        # Add records
        for i in range(3):
            task = Task(
                task_id=f"test-{i}",
                text=f"Task {i}",
                status=TaskStatus.COMPLETED,
                file_path=str(tmp_path / f"test-{i}.mp3"),
            )
            (tmp_path / f"test-{i}.mp3").write_bytes(b"x")
            await service.create_history(task, test_db)

        count = await service.get_history_count(test_db)
        assert count == 3

    @pytest.mark.asyncio
    async def test_auto_cleanup_old_records(self, test_db, tmp_path):
        """Test automatic cleanup of old records."""
        service = HistoryService(max_size=3)

        # Create 5 records (should auto-cleanup to 3)
        for i in range(5):
            task = Task(
                task_id=f"test-{i}",
                text=f"Task {i}",
                status=TaskStatus.COMPLETED,
                file_path=str(tmp_path / f"test-{i}.mp3"),
            )
            (tmp_path / f"test-{i}.mp3").write_bytes(b"x")
            await service.create_history(task, test_db)

        # Should only have 3 (max_size)
        count = await service.get_history_count(test_db)
        assert count <= 3
