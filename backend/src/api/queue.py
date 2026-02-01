"""Queue API endpoints.

Provides REST API for queue status management.
"""

from fastapi import APIRouter

from src.api.schemas import QueueStatusResponse
from src.services.queue_service import queue_service

router = APIRouter(tags=["queue"])


@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status():
    """Get current queue status.

    Returns:
        Queue status information including counts and current task
    """
    status = queue_service.get_status()

    # Get current task details if available
    current_task_response = None
    if status.get("current_task"):
        # Note: In a real implementation, we'd fetch the full task from DB
        # For now, just return the task_id
        current_task_response = None

    return QueueStatusResponse(
        queued_count=status["queued_count"],
        processing_count=status["processing_count"],
        completed_count=status["completed_count"],
        current_task=current_task_response,
        max_queue_size=status["max_queue_size"],
    )
