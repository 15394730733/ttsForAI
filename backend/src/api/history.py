"""History API endpoints.

Provides REST API for TTS generation history management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import HistoryListResponse, HistoryResponse
from src.core.database import get_db
from src.core.logger import logger
from src.services.history_service import HistoryService

router = APIRouter(tags=["history"])

# Initialize service
history_service = HistoryService()


@router.get("/", response_model=HistoryListResponse)
async def get_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get list of history records.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of history records with total count
    """
    try:
        records = await history_service.get_history_list(db, skip=skip, limit=limit)
        total = await history_service.get_history_count(db)

        # Convert to response format
        response_records = [
            HistoryResponse(
                id=record.id,
                task_id=record.task_id,
                text_summary=record.text_summary,
                voice_params=record.voice_params,
                created_at=record.created_at.isoformat() if record.created_at else "",
                file_path=record.file_path,
                filename=getattr(record, 'filename', None),  # Explicitly get filename
                file_size=record.file_size,
                status=record.status,
            )
            for record in records
        ]

        return HistoryListResponse(records=response_records, total=total)

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history records",
        )


@router.delete("/clear")
async def clear_all_history(
    db: AsyncSession = Depends(get_db),
):
    """Clear all history records.

    Args:
        db: Database session

    Returns:
        Deletion result with count
    """
    try:
        count = await history_service.clear_all_history(db, delete_files=True)

        return {
            "deleted_count": count,
            "message": f"已删除 {count} 条历史记录",
        }

    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear history records",
        )


@router.delete("/{history_id}")
async def delete_history_record(
    history_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single history record.

    Args:
        history_id: History record ID
        db: Database session

    Returns:
        Deletion result

    Raises:
        HTTPException: If record not found or deletion fails
    """
    success = await history_service.delete_history(history_id, db, delete_file=True)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record {history_id} not found",
        )

    return {
        "id": history_id,
        "deleted": True,
        "message": f"历史记录 {history_id} 已删除",
    }
