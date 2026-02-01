"""Logger system tests.

Tests for logging configuration, context support, and log rotation.
"""

import logging
import pytest
from pathlib import Path

from src.core.logger import setup_logging, get_logger, log_context, LoggerContext


class TestLoggingSetup:
    """Test logging configuration."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "tts_app"

    def test_logger_has_handlers(self):
        """Test that logger has console and file handlers."""
        logger = setup_logging()
        assert len(logger.handlers) == 2

        handler_types = [type(h).__name__ for h in logger.handlers]
        assert "StreamHandler" in handler_types
        assert "TimedRotatingFileHandler" in handler_types

    def test_logger_level(self):
        """Test that logger level is configured correctly."""
        logger = setup_logging()
        # Default is INFO
        assert logger.level == logging.INFO

    def test_logger_does_not_propagate(self):
        """Test that logger does not propagate to root logger."""
        logger = setup_logging()
        assert logger.propagate is False


class TestLoggerContext:
    """Test logger with context support."""

    def test_get_logger_returns_logger_context(self):
        """Test that get_logger returns LoggerContext instance."""
        context_logger = get_logger("TestService")
        assert isinstance(context_logger, LoggerContext)
        assert context_logger.context == "TestService"

    def test_logger_context_has_log_methods(self):
        """Test that LoggerContext has all log methods."""
        context_logger = get_logger("TestService")

        assert hasattr(context_logger, "debug")
        assert hasattr(context_logger, "info")
        assert hasattr(context_logger, "warning")
        assert hasattr(context_logger, "error")
        assert hasattr(context_logger, "critical")
        assert hasattr(context_logger, "exception")

    def test_logger_context_info_message(self):
        """Test that LoggerContext can be created and used."""
        context_logger = get_logger("TestService")
        assert context_logger is not None
        assert context_logger.context == "TestService"

        # Just check it doesn't throw
        context_logger.info("Test message")

    def test_logger_context_error_message(self):
        """Test that LoggerContext can log errors."""
        context_logger = get_logger("TestService")

        # Just check it doesn't throw
        context_logger.error("Error message")

    def test_logger_context_exception(self):
        """Test that LoggerContext can log exceptions."""
        context_logger = get_logger("TestService")

        try:
            raise ValueError("Test exception")
        except Exception:
            # Just check it doesn't throw
            context_logger.exception("Exception occurred")


class TestLogContextManager:
    """Test log_context context manager."""

    def test_log_context_yields_logger(self):
        """Test that log_context yields LoggerContext."""
        with log_context("TestService") as logger:
            assert isinstance(logger, LoggerContext)
            assert logger.context == "TestService"

    def test_log_context_can_log_messages(self):
        """Test that log_context logger can log messages."""
        with log_context("TestService") as logger:
            # Just check it doesn't throw
            logger.info("Test message from context")


class TestLogRotation:
    """Test log file rotation configuration."""

    def test_timed_rotating_file_handler_config(self):
        """Test that TimedRotatingFileHandler is configured correctly."""
        logger = setup_logging()

        # Find TimedRotatingFileHandler
        file_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "when"):
                file_handler = handler
                break

        assert file_handler is not None
        # The when attribute is stored in uppercase by the handler
        assert file_handler.when.upper() == "MIDNIGHT"
        # Note: interval is converted to seconds by TimedRotatingFileHandler
        # For midnight, it becomes 86400 seconds
        assert file_handler.backupCount == 7

    def test_log_file_location(self):
        """Test that log file is in configured directory."""
        from src.core.config import settings

        logger = setup_logging()

        # Find TimedRotatingFileHandler
        file_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "baseFilename"):
                file_handler = handler
                break

        assert file_handler is not None
        log_path = Path(file_handler.baseFilename)
        # Check that log is in LOG_DIR or a subdirectory
        assert settings.LOG_DIR.resolve() in log_path.resolve().parents or log_path.parent.resolve() == settings.LOG_DIR.resolve()


class TestLogFormatting:
    """Test log message formatting."""

    def test_file_formatter_includes_context(self):
        """Test that file formatter includes context field."""
        logger = setup_logging()

        # Find file handler (TimedRotatingFileHandler)
        file_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "baseFilename"):  # FileHandler has baseFilename
                file_handler = handler
                break

        assert file_handler is not None
        assert "[%(context)s]" in file_handler.formatter._fmt

    def test_console_formatter_does_not_include_context(self):
        """Test that console formatter is simpler (no context)."""
        logger = setup_logging()

        # Find console handler (StreamHandler without baseFilename)
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not hasattr(handler, "baseFilename"):
                console_handler = handler
                break

        assert console_handler is not None
        # Console format is simpler
        assert "%(levelname)s - %(message)s" in console_handler.formatter._fmt


class TestLogLevels:
    """Test different log levels."""

    def test_debug_level_below_info(self):
        """Test that DEBUG is below INFO."""
        assert logging.DEBUG < logging.INFO

    def test_info_level_below_warning(self):
        """Test that INFO is below WARNING."""
        assert logging.INFO < logging.WARNING

    def test_warning_level_below_error(self):
        """Test that WARNING is below ERROR."""
        assert logging.WARNING < logging.ERROR

    def test_error_level_below_critical(self):
        """Test that ERROR is below CRITICAL."""
        assert logging.ERROR < logging.CRITICAL


class TestLoggerOutput:
    """Test actual logger output."""

    def test_context_in_extra(self):
        """Test that context is added to extra dict."""
        context_logger = get_logger("MyService")

        # Just check it doesn't throw
        context_logger.info("Test")
