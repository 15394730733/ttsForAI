"""Test utility functions.

Provides helper functions for creating test data and fixtures.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.history import History
from src.services.queue_service import queue_service


def generate_task_id() -> str:
    """Generate a unique task ID for testing.

    Returns:
        str: Unique task ID
    """
    return str(uuid.uuid4())


def create_test_task_data(override: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Create test task data.

    Args:
        override: Optional dictionary with field overrides

    Returns:
        Dict with test task data
    """
    data = {
        "task_id": generate_task_id(),
        "text": "测试文本",
        "voice_name": "zh-CN-XiaoxiaoNeural",
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "status": "queued",
        "progress": 0,
        "file_path": None,
        "error_message": None,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
    }

    if override:
        data.update(override)

    return data


def create_test_audio_file(output_dir: Path, task_id: str) -> Path:
    """Create a test audio file.

    Args:
        output_dir: Output directory path
        task_id: Task ID for filename

    Returns:
        Path to created test file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    test_file = output_dir / f"{task_id}.mp3"

    # Create a minimal MP3 file (ID3v2 header + dummy data)
    test_file.write_bytes(b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 100)

    return test_file


def validate_task_response(response: Dict[str, Any]) -> bool:
    """Validate task response structure.

    Args:
        response: Task response dict

    Returns:
        True if valid
    """
    required_fields = [
        "task_id",
        "text",
        "voice_name",
        "rate",
        "pitch",
        "volume",
        "status",
        "progress",
        "created_at",
    ]

    return all(field in response for field in required_fields)


# ==================== Test Cleanup Functions ====================


async def clear_test_database(db: AsyncSession) -> None:
    """Clear all test data from database.

    Args:
        db: Database session
    """
    # Delete all history records first (foreign key dependency)
    await db.execute(delete(History))
    # Delete all tasks
    await db.execute(delete(Task))
    await db.commit()


def clear_test_queue() -> None:
    """Clear the test queue."""
    # Import asyncio to run async function
    import asyncio

    # Try to clear the queue synchronously
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create task
            asyncio.create_task(queue_service.clear_queue())
        else:
            # If loop is not running, run directly
            loop.run_until_complete(queue_service.clear_queue())
    except:
        # If all else fails, ignore the error
        # The queue will be cleaned up between test sessions
        pass


async def reset_test_state(db: AsyncSession) -> None:
    """Reset all test state (database and queue).

    Args:
        db: Database session
    """
    # Clear database
    await clear_test_database(db)

    # Clear queue
    clear_test_queue()
