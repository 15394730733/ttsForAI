"""Unit tests for TTS service.

Tests TTS service functionality with mocked edge-tts engine.
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.models.task import Task, TaskStatus
from src.services.tts_service import TTSService


class TestTTSService:
    """Test TTS service."""

    def test_init(self, tmp_path):
        """Test TTSService initialization."""
        service = TTSService(output_dir=tmp_path)

        assert service.output_dir == tmp_path
        assert service.output_dir.exists()

    @pytest.mark.asyncio
    async def test_generate_audio_success(self, tmp_path):
        """Test successful audio generation."""
        # Create service
        service = TTSService(output_dir=tmp_path)

        # Create task
        task = Task(
            task_id="test-001",
            text="Hello, world!",
            voice_name="zh-CN-XiaoxiaoNeural",
            rate=1.0,
            pitch=1.0,
            volume=1.0,
        )

        # Mock edge-tts Communicate
        async def mock_save(file_path):
            # Actually create the file
            Path(file_path).write_bytes(b"mock audio data")

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock(side_effect=mock_save)

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Generate audio
            result = await service.generate_audio(task)

        # Verify
        assert task.status == TaskStatus.COMPLETED
        assert task.progress == 100
        assert task.file_path is not None
        assert task.started_at is not None
        assert task.completed_at is not None

        # Check file was created
        output_file = Path(result)
        assert output_file.exists()
        assert output_file.name == "test-001.mp3"

    @pytest.mark.asyncio
    async def test_generate_audio_with_progress_callback(self, tmp_path):
        """Test audio generation with progress callback."""
        service = TTSService(output_dir=tmp_path)

        task = Task(
            task_id="test-002",
            text="Test with progress",
        )

        progress_updates = []

        async def progress_callback(progress):
            progress_updates.append(progress)

        # Mock edge-tts to actually create the file
        async def mock_save(file_path):
            Path(file_path).write_bytes(b"mock audio data")

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock(side_effect=mock_save)

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            await service.generate_audio(task, progress_callback=progress_callback)

        # Verify progress was reported
        assert len(progress_updates) > 0
        assert 100 in progress_updates  # Should reach 100%

    @pytest.mark.asyncio
    async def test_generate_audio_failure(self, tmp_path):
        """Test audio generation failure handling."""
        service = TTSService(output_dir=tmp_path)

        task = Task(
            task_id="test-003",
            text="Test failure",
        )

        # Mock edge-tts Communicate __init__ to raise exception
        def mock_communicate_init_error(*args, **kwargs):
            raise Exception("Network error")

        with patch("edge_tts.Communicate", side_effect=mock_communicate_init_error):
            try:
                await service.generate_audio(task)
            except Exception:
                pass  # Expected

        # Verify error handling - task should be marked as failed
        assert task.status == TaskStatus.FAILED
        assert task.error_message is not None
        assert task.completed_at is not None

    @pytest.mark.asyncio
    async def test_generate_audio_simple(self, tmp_path):
        """Test simple audio generation without task tracking."""
        service = TTSService(output_dir=tmp_path)

        # Mock edge-tts to create actual file
        async def mock_save(file_path):
            Path(file_path).write_bytes(b"mock audio data")

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock(side_effect=mock_save)

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            task_id, file_path = await service.generate_audio_simple(
                text="Simple test",
                voice_name="zh-CN-XiaoxiaoNeural",
            )

        # Verify
        assert task_id is not None
        assert file_path is not None
        assert Path(file_path).exists()

    def test_get_audio_file_path(self, tmp_path):
        """Test getting audio file path."""
        service = TTSService(output_dir=tmp_path)

        file_path = service.get_audio_file_path("test-004")

        assert file_path == tmp_path / "test-004.mp3"

    @pytest.mark.asyncio
    async def test_audio_file_exists(self, tmp_path):
        """Test checking if audio file exists."""
        service = TTSService(output_dir=tmp_path)

        # Create a test file
        test_file = tmp_path / "test-005.mp3"
        test_file.write_text("mock audio data")

        # Check exists
        assert service.audio_file_exists("test-005") is True
        assert service.audio_file_exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_delete_audio_file(self, tmp_path):
        """Test deleting audio file."""
        service = TTSService(output_dir=tmp_path)

        # Create a test file
        test_file = tmp_path / "test-006.mp3"
        test_file.write_text("mock audio data")

        # Delete
        result = service.delete_audio_file("test-006")

        assert result is True
        assert test_file.exists() is False

        # Delete non-existent file
        result = service.delete_audio_file("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_audio_params_passed_to_edge_tts(self, tmp_path):
        """Test that voice parameters are correctly passed to edge-tts."""
        service = TTSService(output_dir=tmp_path)

        task = Task(
            task_id="test-007",
            text="Param test",
            voice_name="zh-CN-YunyangNeural",
            rate=1.5,
            pitch=0.8,
            volume=0.9,
        )

        # Capture Communicate initialization
        communicate_init_calls = []

        class MockCommunicate:
            def __init__(self, *args, **kwargs):
                communicate_init_calls.append((args, kwargs))

            async def save(self, file_path):
                # Create the file
                Path(file_path).write_bytes(b"mock audio data")

        with patch("edge_tts.Communicate", MockCommunicate):
            await service.generate_audio(task)

        # Verify Communicate was initialized with correct parameters
        assert len(communicate_init_calls) == 1
        args, kwargs = communicate_init_calls[0]

        # Check text parameter (keyword argument)
        assert 'text' in kwargs
        assert kwargs['text'] == "Param test"

        # Check voice parameter (keyword argument)
        assert 'voice' in kwargs
        assert kwargs['voice'] == "zh-CN-YunyangNeural"

        # Check rate, pitch, volume parameters
        assert 'rate' in kwargs
        assert 'pitch' in kwargs
        assert 'volume' in kwargs
