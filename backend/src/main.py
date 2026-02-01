"""
FastAPI application entry point.

Main application factory with CORS, middleware, and route registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import health, history, queue, tts
from .core.config import settings
from .core.database import engine, init_database
from .core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting TTS Service...")
    await init_database()
    logger.info("Database initialized")

    # Start queue processor
    from .services.queue_processor import queue_processor

    await queue_processor.start()
    logger.info("Queue processor started")

    yield

    # Shutdown
    logger.info("Shutting down TTS Service...")
    await queue_processor.stop()
    logger.info("Queue processor stopped")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="TTS Service",
    description="离线文字转语音工具 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routes
app.include_router(health.router)
app.include_router(tts.router, prefix="/api/v1/tts")
app.include_router(queue.router, prefix="/api/v1/queue")
app.include_router(history.router, prefix="/api/v1/history")


# ==================== Global Exception Handlers ====================


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"ValueError in {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "ValidationError", "message": str(exc)},
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle PermissionError exceptions."""
    logger.error(f"PermissionError in {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "PermissionError", "message": str(exc)},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle FileNotFoundError exceptions."""
    logger.warning(f"FileNotFoundError in {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "FileNotFound", "message": "Requested file not found"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception in {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
