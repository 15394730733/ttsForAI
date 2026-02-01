"""File storage service.

Manages audio file storage, retrieval, and cleanup.
"""

from pathlib import Path

from src.core.config import settings
from src.core.logger import logger


class StorageService:
    """Service for managing audio file storage."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize storage service.

        Args:
            output_dir: Directory for audio files (default: from settings)
        """
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_file_path(self, task_id: str, extension: str = "mp3") -> Path:
        """Generate file path for a task.

        Args:
            task_id: Task identifier
            extension: File extension (default: mp3)

        Returns:
            Path to audio file
        """
        return self.output_dir / f"{task_id}.{extension}"

    def save_file(self, content: bytes, filename: str) -> Path:
        """Save file content to disk.

        Args:
            content: File content as bytes
            filename: Name of the file

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be saved
        """
        file_path = self.output_dir / filename

        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logger.info(f"Saved file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            raise OSError(f"Failed to save file: {e}")

    def get_file(self, task_id: str) -> Path | None:
        """Get file path for task.

        Args:
            task_id: Task identifier

        Returns:
            Path to file if exists, None otherwise
        """
        file_path = self.generate_file_path(task_id)
        return file_path if file_path.exists() else None

    def file_exists(self, task_id: str) -> bool:
        """Check if file exists for task.

        Args:
            task_id: Task identifier

        Returns:
            True if file exists
        """
        return self.generate_file_path(task_id).exists()

    def get_file_size(self, task_id: str) -> int | None:
        """Get file size in bytes.

        Args:
            task_id: Task identifier

        Returns:
            File size in bytes, None if file doesn't exist
        """
        file_path = self.get_file(task_id)
        if file_path:
            return file_path.stat().st_size
        return None

    def delete_file(self, task_id: str) -> bool:
        """Delete file for task.

        Args:
            task_id: Task identifier

        Returns:
            True if file was deleted, False otherwise
        """
        file_path = self.get_file(task_id)
        if file_path:
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete file {task_id}: {e}")
                return False
        return False

    def list_files(self) -> list[Path]:
        """List all files in output directory.

        Returns:
            List of file paths
        """
        return [f for f in self.output_dir.iterdir() if f.is_file()]

    def get_total_size(self) -> int:
        """Get total size of all files in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for file_path in self.list_files():
            total += file_path.stat().st_size
        return total

    def cleanup_old_files(self, max_age_days: int = 7) -> int:
        """Delete files older than specified days.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of files deleted
        """
        import time

        cutoff_time = time.time() - (max_age_days * 86400)
        deleted_count = 0

        for file_path in self.list_files():
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete old file {file_path}: {e}")

        return deleted_count

    def clear_all(self) -> int:
        """Delete all files in output directory.

        Returns:
            Number of files deleted

        Caution:
            This will delete ALL files without confirmation
        """
        deleted_count = 0
        for file_path in self.list_files():
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

        logger.info(f"Cleared {deleted_count} files from output directory")
        return deleted_count
