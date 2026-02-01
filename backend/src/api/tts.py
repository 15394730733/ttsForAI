"""TTS API endpoints.

Provides REST API for TTS generation and management.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    TaskCreateRequest,
    TaskResponse,
    VoiceInfo,
    VoicesResponse,
)
from src.api.schemas import (
    validate_voice_name as schema_validate_voice_name,
)
from src.core.config import get_all_voices, settings
from src.core.database import get_db
from src.core.logger import logger
from src.core.security import sanitize_text, validate_text_length
from src.models.task import Task, TaskStatus
from src.services.queue_service import queue_service
from src.services.tts_service import TTSService

router = APIRouter(tags=["tts"])

# Initialize services
tts_service = TTSService()


@router.post(
    "/generate", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create new TTS generation task.

    Args:
        request: Task creation request
        db: Database session

    Returns:
        Created task information

    Raises:
        HTTPException: If validation fails or queue is full
    """
    # Validate input
    if not validate_text_length(request.text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text must be 1-5000 characters",
        )

    # Sanitize text
    try:
        sanitized_text = sanitize_text(request.text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Validate voice name
    try:
        voice_name = schema_validate_voice_name(request.voice_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Check queue capacity
    if queue_service.is_full():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Queue is full ({queue_service.max_size} tasks)",
        )

    # Create task
    task_id = str(uuid.uuid4())
    task = Task(
        task_id=task_id,
        text=sanitized_text,
        voice_name=voice_name,
        rate=request.rate,
        pitch=request.pitch,
        volume=request.volume,
        status=TaskStatus.QUEUED,
        progress=0,
    )

    # Add to database
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Add to queue (will be processed by queue processor)
    await queue_service.enqueue(task)

    logger.info(f"Created task {task_id}")

    return TaskResponse(
        task_id=task.task_id,
        text=task.text,
        voice_name=task.voice_name,
        rate=task.rate,
        pitch=task.pitch,
        volume=task.volume,
        status=task.status,
        progress=task.progress,
        file_path=task.file_path,
        error_message=task.error_message,
        created_at=task.created_at.isoformat() if task.created_at else "",
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get task information by ID.

    Args:
        task_id: Task identifier
        db: Database session

    Returns:
        Task information

    Raises:
        HTTPException: If task not found
    """
    result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse(
        task_id=task.task_id,
        text=task.text,
        voice_name=task.voice_name,
        rate=task.rate,
        pitch=task.pitch,
        volume=task.volume,
        status=task.status,
        progress=task.progress,
        file_path=task.file_path,
        error_message=task.error_message,
        created_at=task.created_at.isoformat() if task.created_at else "",
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a queued task.

    Args:
        task_id: Task identifier
        db: Database session

    Returns:
        Cancellation result

    Raises:
        HTTPException: If task not found or cannot be cancelled
    """
    success = await queue_service.cancel_task(task_id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task not found or cannot be cancelled",
        )

    return {"task_id": task_id, "status": "cancelled"}


@router.get("/download/{task_id}")
async def download_audio(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download generated audio file.

    Args:
        task_id: Task identifier
        db: Database session

    Returns:
        Audio file response

    Raises:
        HTTPException: If task not found or file not available
    """
    result = await db.execute(select(Task).where(Task.task_id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.status != TaskStatus.COMPLETED or not task.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file not ready",
        )

    file_path = Path(task.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=f"{task_id}.mp3",
    )


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """Get list of available voices.

    Returns:
        List of available voices with name, ID, and description
    """
    voices = []
    all_voices = get_all_voices()

    for name, voice_id in all_voices.items():
        is_default = voice_id == settings.DEFAULT_VOICE
        description = "默认女声" if is_default else f"{name}"

        voices.append(
            VoiceInfo(
                name=name,
                voice_id=voice_id,
                description=description,
                default=is_default,
            )
        )

    return VoicesResponse(voices=voices)
