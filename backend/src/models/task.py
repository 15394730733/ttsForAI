"""Task ORM model.

Represents a TTS generation task with its status and metadata.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class TaskStatus:
    """Task status constants."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base, TimestampMixin):
    """TTS generation task model.

    Attributes:
        task_id: Unique task identifier (UUID)
        text: Input text to convert to speech
        voice_name: Selected voice for TTS
        rate: Speech rate multiplier (0.5-2.0)
        pitch: Pitch multiplier (0.5-2.0)
        volume: Volume level (0.0-1.0)
        status: Current task status
        progress: Generation progress (0-100)
        file_path: Path to generated audio file (nullable)
        error_message: Error message if failed (nullable)
        created_at: Task creation timestamp
        started_at: Task start timestamp (nullable)
        completed_at: Task completion timestamp (nullable)
    """

    __tablename__ = "tasks"

    # Primary key
    task_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    # Input parameters
    text: Mapped[str] = mapped_column(Text, nullable=False)
    voice_name: Mapped[str] = mapped_column(
        String(100), nullable=False, default="zh-CN-XiaoxiaoNeural"
    )
    rate: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    pitch: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Status fields
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.QUEUED,
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Output fields
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Actual filename used (without .mp3 extension)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """String representation of Task."""
        return f"<Task(task_id={self.task_id}, status={self.status}, text={self.text[:50]}...)>"

    def to_dict(self) -> dict:
        """Convert task to dictionary.

        Returns:
            dict: Task data as dictionary
        """
        return {
            "task_id": self.task_id,
            "text": self.text,
            "voice_name": self.voice_name,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "status": self.status,
            "progress": self.progress,
            "file_path": self.file_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
