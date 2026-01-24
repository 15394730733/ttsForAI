"""
Logging configuration.

Provides structured logging with file rotation.
"""
import logging
import logging.handlers
from pathlib import Path

from .config import settings


def setup_logging() -> logging.Logger:
    """
    Setup application logging with file rotation.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if not exists
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger("tts_app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    # File handler with daily rotation
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=settings.LOG_DIR / "tts_app.log",
        when="midnight",
        interval=1,
        backupCount=7,  # Keep 7 days of logs
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logging()
