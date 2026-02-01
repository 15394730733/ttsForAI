"""History ORM model.

Represents a record of completed TTS generation in the history.
"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class History(Base, TimestampMixin):
    """TTS generation history model.

    Stores records of successfully completed TTS generations
    for later retrieval and download.

    Attributes:
        id: Auto-increment primary key
        task_id: Reference to the original task
        text_summary: Summary of the input text (first 100 chars)
        voice_params: JSON string of voice parameters used
        created_at: Record creation timestamp
        file_path: Path to the generated audio file
        file_size: Size of the generated file in bytes
        status: Status of the history record
    """

    __tablename__ = "history"

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Task reference
    task_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True
    )

    # Content
    text_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    voice_params: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string

    # File info
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Actual filename used (without extension)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    def __repr__(self) -> str:
        """String representation of History."""
        return f"<History(id={self.id}, task_id={self.task_id}, text={self.text_summary[:30]}...)>"

    def to_dict(self) -> dict:
        """Convert history record to dictionary.

        Returns:
            dict: History data as dictionary
        """
        return {
            "id": self.id,
            "task_id": self.task_id,
            "text_summary": self.text_summary,
            "voice_params": self.voice_params,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "file_path": self.file_path,
            "filename": self.filename,
            "file_size": self.file_size,
            "status": self.status,
        }
