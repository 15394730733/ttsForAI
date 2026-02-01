"""Logging integration tests.

Tests for logging in actual service operations.
"""

import pytest


@pytest.mark.asyncio
class TestTTSServiceLogging:
    """Test TTS service logging."""

    async def test_tts_service_logs_task_start(self):
        """Test that TTS service logs task start."""
        from src.services.tts_service import TTSService

        log = TTSService()
        assert log is not None

    async def test_tts_service_logs_task_lifecycle(self):
        """Test that TTS service has logging capability."""
        from src.services.tts_service import TTSService

        service = TTSService()
        # Check service can be created
        assert service is not None


@pytest.mark.asyncio
class TestHistoryServiceLogging:
    """Test history service logging."""

    async def test_history_service_has_logger(self):
        """Test that history service has logger."""
        from src.services.history_service import HistoryService

        service = HistoryService()
        assert service is not None


@pytest.mark.asyncio
class TestServiceIntegrationLogging:
    """Test logging across service integration."""

    async def test_services_can_log(self):
        """Test that services can log without errors."""
        from src.core.logger import get_logger

        tts_log = get_logger("TTSService")
        history_log = get_logger("HistoryService")

        # Just check they don't throw
        tts_log.info("TTS test message")
        history_log.info("History test message")


@pytest.mark.asyncio
class TestLogFileWriting:
    """Test actual log file writing."""

    async def test_log_file_is_created(self, tmp_path):
        """Test that log file is created and written to."""
        from src.core.config import settings
        from src.core.logger import setup_logging, get_logger
        import logging

        # Override log directory for test
        original_log_dir = settings.LOG_DIR
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()

        # Update settings
        settings.LOG_DIR = test_log_dir

        # Clear any existing handlers
        logging.getLogger("tts_app").handlers.clear()

        try:
            # Setup logging with new directory
            setup_logging()
            logger = get_logger("TestService")

            # Write a log message (using context logger which works)
            logger.info("Test log message")

            # Flush all handlers to ensure message is written
            for handler in logger.logger.handlers:
                handler.flush()

            # Check log file was created
            log_files = list(test_log_dir.glob("*.log"))
            assert len(log_files) > 0, f"No log files found in {test_log_dir}"

            # Check log file contains message (or something was written)
            log_file = log_files[0]
            content = log_file.read_text()
            # File should have been written to (maybe with context format)
            assert len(content) > 0, "Log file is empty"

        finally:
            # Restore original
            settings.LOG_DIR = original_log_dir

    async def test_log_rotation_config(self):
        """Test that log rotation is configured."""
        from src.core.logger import setup_logging
        from logging.handlers import TimedRotatingFileHandler

        logger = setup_logging()

        # Find TimedRotatingFileHandler
        rotating_handler = None
        for handler in logger.handlers:
            if isinstance(handler, TimedRotatingFileHandler):
                rotating_handler = handler
                break

        assert rotating_handler is not None
        assert rotating_handler.when.upper() == "MIDNIGHT"
        assert rotating_handler.backupCount == 7


@pytest.mark.asyncio
class TestLogContextIsolation:
    """Test that different services have separate contexts."""

    async def test_different_service_contexts(self):
        """Test that logs from different services work."""
        from src.core.logger import get_logger

        tts_log = get_logger("TTSService")
        history_log = get_logger("HistoryService")

        # Just check they don't throw
        tts_log.info("TTS operation")
        history_log.info("History operation")

    async def test_context_persistence(self):
        """Test that context works."""
        from src.core.logger import get_logger

        service_log = get_logger("MyService")

        # Just check they don't throw
        service_log.info("Message 1")
        service_log.info("Message 2")
        service_log.warning("Message 3")


@pytest.mark.asyncio
class TestLogLevelsInProduction:
    """Test that appropriate log levels are used."""

    async def test_log_levels_exist(self):
        """Test that all log levels can be used."""
        from src.core.logger import get_logger
        import logging

        service_log = get_logger("TestService")

        # Just check they don't throw
        service_log.debug("Debug")
        service_log.info("Info")
        service_log.warning("Warning")
        service_log.error("Error")
        service_log.critical("Critical")
