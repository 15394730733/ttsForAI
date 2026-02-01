"""Unit tests for Storage service.

Tests file storage and management functionality.
"""
import pytest
from pathlib import Path

from src.services.storage_service import StorageService


class TestStorageService:
    """Test Storage service."""

    def test_init(self, tmp_path):
        """Test StorageService initialization."""
        service = StorageService(output_dir=tmp_path)

        assert service.output_dir == tmp_path
        assert service.output_dir.exists()

    def test_generate_file_path(self, tmp_path):
        """Test file path generation."""
        service = StorageService(output_dir=tmp_path)

        file_path = service.generate_file_path("test-001")

        assert file_path == tmp_path / "test-001.mp3"

    def test_generate_file_path_custom_extension(self, tmp_path):
        """Test file path generation with custom extension."""
        service = StorageService(output_dir=tmp_path)

        file_path = service.generate_file_path("test-002", extension="wav")

        assert file_path == tmp_path / "test-002.wav"

    def test_save_file(self, tmp_path):
        """Test saving file to disk."""
        service = StorageService(output_dir=tmp_path)

        content = b"mock audio data"
        file_path = service.save_file(content, "test-003.mp3")

        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_save_file_creates_directory(self, tmp_path):
        """Test that save_file creates output directory if needed."""
        new_dir = tmp_path / "new_output"
        service = StorageService(output_dir=new_dir)

        content = b"test data"
        file_path = service.save_file(content, "test-004.mp3")

        assert new_dir.exists()
        assert file_path.exists()

    def test_get_file(self, tmp_path):
        """Test getting file path."""
        service = StorageService(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test-005.mp3"
        test_file.write_bytes(b"audio data")

        # Get file
        file_path = service.get_file("test-005")

        assert file_path is not None
        assert file_path == test_file

    def test_get_file_not_found(self, tmp_path):
        """Test getting non-existent file."""
        service = StorageService(output_dir=tmp_path)

        file_path = service.get_file("nonexistent")

        assert file_path is None

    def test_file_exists(self, tmp_path):
        """Test checking if file exists."""
        service = StorageService(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test-006.mp3"
        test_file.write_bytes(b"audio")

        assert service.file_exists("test-006") is True
        assert service.file_exists("nonexistent") is False

    def test_get_file_size(self, tmp_path):
        """Test getting file size."""
        service = StorageService(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test-007.mp3"
        test_file.write_bytes(b"x" * 1000)  # 1000 bytes

        size = service.get_file_size("test-007")

        assert size == 1000

    def test_get_file_size_not_found(self, tmp_path):
        """Test getting size of non-existent file."""
        service = StorageService(output_dir=tmp_path)

        size = service.get_file_size("nonexistent")

        assert size is None

    def test_delete_file(self, tmp_path):
        """Test deleting file."""
        service = StorageService(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test-008.mp3"
        test_file.write_bytes(b"audio")

        # Delete
        result = service.delete_file("test-008")

        assert result is True
        assert test_file.exists() is False

    def test_delete_file_not_found(self, tmp_path):
        """Test deleting non-existent file."""
        service = StorageService(output_dir=tmp_path)

        result = service.delete_file("nonexistent")

        assert result is False

    def test_list_files(self, tmp_path):
        """Test listing all files."""
        service = StorageService(output_dir=tmp_path)

        # Create test files
        (tmp_path / "test1.mp3").write_bytes(b"audio1")
        (tmp_path / "test2.mp3").write_bytes(b"audio2")

        files = service.list_files()

        assert len(files) == 2
        assert all(f.is_file() for f in files)

    def test_get_total_size(self, tmp_path):
        """Test getting total size of all files."""
        service = StorageService(output_dir=tmp_path)

        # Create test files
        (tmp_path / "test1.mp3").write_bytes(b"x" * 1000)
        (tmp_path / "test2.mp3").write_bytes(b"x" * 2000)

        total = service.get_total_size()

        assert total == 3000

    def test_cleanup_old_files(self, tmp_path):
        """Test cleaning up old files."""
        service = StorageService(output_dir=tmp_path)

        # Create old file (simulate by not touching it)
        # In real test, we'd mock time.time()
        # For now, just test the method doesn't crash
        count = service.cleanup_old_files(max_age_days=7)

        # Should return 0 as no old files
        assert count == 0

    def test_clear_all(self, tmp_path):
        """Test clearing all files."""
        service = StorageService(output_dir=tmp_path)

        # Create test files
        (tmp_path / "test1.mp3").write_bytes(b"audio1")
        (tmp_path / "test2.mp3").write_bytes(b"audio2")

        # Clear all
        count = service.clear_all()

        assert count == 2
        assert len(service.list_files()) == 0
