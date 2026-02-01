"""History management integration tests.

Tests for history record management including creation,
auto-cleanup, and deletion functionality.
"""

import pytest
from pathlib import Path

from src.models.task import Task, TaskStatus
from src.services.history_service import HistoryService


@pytest.mark.asyncio
class TestHistoryManagement:
    """Test history management features."""

    async def test_history_creation_from_completed_task(self, test_db, tmp_path):
        """Test creating history record from completed task."""
        service = HistoryService()

        # Create a completed task
        task = Task(
            task_id="hist_task1",
            text="This is a test text for history",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task.status = TaskStatus.COMPLETED
        task.file_path = str(tmp_path / "test_audio.mp3")

        # Create a dummy audio file
        task.file_path = str(tmp_path / "test_audio.mp3")
        Path(task.file_path).write_bytes(b"fake audio data")

        # Create history record
        history = await service.create_history(task, test_db)

        assert history is not None
        assert history.task_id == "hist_task1"
        assert history.text_summary == "This is a test text for history"
        assert "zh-CN-XiaoxiaoNeural" in history.voice_params
        assert history.file_path == task.file_path
        assert history.status == "active"

    async def test_history_list_pagination(self, test_db, tmp_path):
        """Test history list with pagination."""
        # Use larger max_size to avoid auto-cleanup during test
        service = HistoryService(max_size=100)

        # Create 25 history records
        for i in range(25):
            task = Task(
                task_id=f"hist_task_{i}",
                text=f"Test text number {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            task.status = TaskStatus.COMPLETED
            task.file_path = str(tmp_path / f"audio_{i}.mp3")
            Path(task.file_path).write_bytes(b"fake audio")

            await service.create_history(task, test_db)

        # Test first page
        page1 = await service.get_history_list(test_db, skip=0, limit=20)
        assert len(page1) == 20

        # Test second page
        page2 = await service.get_history_list(test_db, skip=20, limit=20)
        assert len(page2) == 5

        # Verify total count
        total = await service.get_history_count(test_db)
        assert total == 25

    async def test_auto_cleanup_old_records(self, test_db, tmp_path):
        """Test automatic cleanup of old records (FIFO)."""
        # Use larger max_size to test cleanup properly
        service = HistoryService(max_size=20)

        # Create 25 records (max is 20)
        for i in range(25):
            task = Task(
                task_id=f"cleanup_task_{i}",
                text=f"Text {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            task.status = TaskStatus.COMPLETED
            task.file_path = str(tmp_path / f"cleanup_{i}.mp3")
            Path(task.file_path).write_bytes(b"fake audio")

            await service.create_history(task, test_db)

        # Should have max 20 records
        total = await service.get_history_count(test_db)
        assert total == 20, f"Expected 20 records but got {total}"

        # Oldest records (0-4) should be deleted
        remaining = await service.get_history_list(test_db, skip=0, limit=25)
        task_ids = [h.task_id for h in remaining]

        # First 5 should be gone (they were auto-cleaned)
        assert "cleanup_task_0" not in task_ids
        assert "cleanup_task_4" not in task_ids

        # Last 5 should still be there
        assert "cleanup_task_20" in task_ids
        assert "cleanup_task_24" in task_ids

    async def test_delete_single_record(self, test_db, tmp_path):
        """Test deleting a single history record."""
        service = HistoryService()

        # Create a record
        task = Task(
            task_id="delete_task",
            text="To be deleted",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task.status = TaskStatus.COMPLETED
        task.file_path = str(tmp_path / "delete_audio.mp3")
        Path(task.file_path).write_bytes(b"fake audio")

        history = await service.create_history(task, test_db)
        history_id = history.id

        # Verify it exists
        found = await service.get_history_by_id(history_id, test_db)
        assert found is not None
        assert found.task_id == "delete_task"

        # Delete it
        success = await service.delete_history(history_id, test_db, delete_file=True)

        assert success is True
        assert Path(task.file_path).exists() is False

        # Verify it's gone
        found = await service.get_history_by_id(history_id, test_db)
        assert found is None

    async def test_clear_all_history(self, test_db, tmp_path):
        """Test clearing all history records."""
        service = HistoryService()

        # Create multiple records
        file_paths = []
        for i in range(10):
            task = Task(
                task_id=f"clear_task_{i}",
                text=f"Text {i}",
                voice_name="zh-CN-XiaoxiaoNeural",
                rate=1.0,
                pitch=1.0,
                volume=1.0,
            )
            task.status = TaskStatus.COMPLETED
            task.file_path = str(tmp_path / f"clear_{i}.mp3")
            Path(task.file_path).write_bytes(b"fake audio")
            file_paths.append(task.file_path)

            await service.create_history(task, test_db)

        # Verify records exist
        total = await service.get_history_count(test_db)
        assert total == 10

        # Clear all
        deleted_count = await service.clear_all_history(test_db, delete_files=True)

        assert deleted_count == 10

        # Verify all records are gone
        total = await service.get_history_count(test_db)
        assert total == 0

        # Verify all files are deleted
        for fp in file_paths:
            assert Path(fp).exists() is False

    async def test_history_from_incomplete_task(self, test_db):
        """Test that incomplete tasks don't create history."""
        service = HistoryService()

        # Create failed task
        task = Task(
            task_id="failed_task",
            text="This failed",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task.status = TaskStatus.FAILED
        task.error_message = "TTS generation failed"

        # Should not create history
        history = await service.create_history(task, test_db)

        assert history is None

    async def test_text_summary_truncation(self, test_db, tmp_path):
        """Test that long text is summarized in history."""
        service = HistoryService()

        # Create task with very long text
        long_text = "A" * 200  # Much longer than typical summary
        task = Task(
            task_id="summary_task",
            text=long_text,
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task.status = TaskStatus.COMPLETED
        task.file_path = str(tmp_path / "summary.mp3")
        Path(task.file_path).write_bytes(b"fake audio")

        history = await service.create_history(task, test_db)

        # Summary should be truncated (100 chars + "..." = 103 max)
        assert len(history.text_summary) <= 103
        assert history.text_summary.startswith("AAAAA")
        assert history.text_summary.endswith("...")

    async def test_text_summary_truncation(self, test_db, tmp_path):
        """Test that long text is summarized in history."""
        service = HistoryService()

        # Create task with very long text
        long_text = "A" * 200  # Much longer than typical summary
        task = Task(
            task_id="summary_task",
            text=long_text,
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )
        task.status = TaskStatus.COMPLETED
        task.file_path = str(tmp_path / "summary.mp3")
        Path(task.file_path).write_bytes(b"fake audio")

        history = await service.create_history(task, test_db)

        # Summary should be truncated (100 chars + "..." = 103 max)
        assert len(history.text_summary) <= 103
        assert history.text_summary.startswith("AAAAA")
        assert history.text_summary.endswith("...")
