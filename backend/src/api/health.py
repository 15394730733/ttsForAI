"""
Health check API endpoints.

Provides system health status and connectivity checks.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.logger import logger

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "tts-api",
        "version": "1.0.0",
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with database connectivity.

    Args:
        db: Database session

    Returns:
        dict: Detailed health status
    """
    health_status = {
        "status": "healthy",
        "service": "tts-api",
        "version": "1.0.0",
        "database": {
            "status": "unknown",
            "message": "Not checked",
        },
        "tts_engine": {
            "status": "ready",
            "name": "edge-tts",
        },
    }

    # Check database connectivity
    try:
        await db.execute(select(func.count()).select_from(text("sqlite_master")))
        health_status["database"] = {
            "status": "connected",
            "message": "Database connection successful",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "degraded"
        health_status["database"] = {
            "status": "disconnected",
            "message": str(e),
        }

    return health_status
