"""
Logging configuration.

Provides structured logging with file rotation and context support.
"""

import logging
import logging.handlers
from collections.abc import Generator
from contextlib import contextmanager

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

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

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
        "%(asctime)s - %(name)s - %(levelname)s - [%(context)s] - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Global logger instance
logger = setup_logging()


class LoggerContext:
    """Adapter for adding context to log records."""

    def __init__(self, logger: logging.Logger, context: str):
        """Initialize with logger and context string.

        Args:
            logger: Logger instance
            context: Context string to add to all log messages
        """
        self.logger = logger
        self.context = context

    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log message with context added.

        Args:
            level: Log level (logging.INFO, etc.)
            msg: Log message
            *args: Additional args
            **kwargs: Additional kwargs (extra dict for context)
        """
        extra = kwargs.pop("extra", {})
        extra["context"] = self.context
        kwargs["extra"] = extra
        self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)


def get_logger(context: str) -> LoggerContext:
    """
    Get a logger with context.

    Args:
        context: Context string (e.g., "TaskService", "HistoryService")

    Returns:
        LoggerContext: Logger with context added to all messages
    """
    return LoggerContext(logger, context)


@contextmanager
def log_context(context: str) -> Generator[LoggerContext, None, None]:
    """
    Context manager for temporary logger context.

    Args:
        context: Context string

    Yields:
        LoggerContext: Logger with context

    Example:
        with log_context("TaskProcessor") as log:
            log.info("Processing task")
    """
    yield get_logger(context)
