"""Security validation tests.

Tests for input sanitization, path traversal protection, and command injection prevention.
"""

import pytest
from pathlib import Path

from src.core.security import (
    sanitize_text,
    validate_text_length,
    sanitize_file_path,
    validate_voice_name,
    sanitize_filename,
    MAX_TEXT_LENGTH,
)


class TestTextSanitization:
    """Test text sanitization functions."""

    def test_sanitize_valid_text(self):
        """Test sanitizing valid text."""
        text = "Hello, world! 你好，世界！"
        result = sanitize_text(text)
        assert result == text

    def test_sanitize_text_with_null_bytes(self):
        """Test removing null bytes from text."""
        text = "Hello\x00World"
        result = sanitize_text(text)
        assert result == "HelloWorld"
        assert "\x00" not in result

    def test_sanitize_text_with_path_traversal(self):
        """Test rejecting path traversal patterns."""
        malicious_texts = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "../sensitive.txt",
            "....// passwd",
        ]

        for text in malicious_texts:
            with pytest.raises(ValueError, match="path traversal"):
                sanitize_text(text)

    def test_sanitize_text_with_control_chars(self):
        """Test rejecting control characters."""
        malicious_texts = [
            "Hello\x01World",
            "Test\x02String",
            "Text\x1fControl",
        ]

        for text in malicious_texts:
            with pytest.raises(ValueError, match="control characters"):
                sanitize_text(text)

    def test_validate_text_length_valid(self):
        """Test valid text length."""
        assert validate_text_length("A" * 1) is True
        assert validate_text_length("A" * MAX_TEXT_LENGTH) is True
        assert validate_text_length("A" * 1000) is True

    def test_validate_text_length_invalid(self):
        """Test invalid text length."""
        assert validate_text_length("") is False
        assert validate_text_length("A" * (MAX_TEXT_LENGTH + 1)) is False

    def test_max_text_length_constant(self):
        """Test MAX_TEXT_LENGTH constant."""
        assert MAX_TEXT_LENGTH == 5000


class TestFilePathSanitization:
    """Test file path sanitization."""

    def test_sanitize_valid_file_path(self, tmp_path):
        """Test sanitizing valid file path."""
        allowed_dir = tmp_path / "output"
        allowed_dir.mkdir()

        result = sanitize_file_path("test.mp3", allowed_dir)
        assert result == (allowed_dir / "test.mp3").resolve()

    def test_sanitize_path_traversal_attempt(self, tmp_path):
        """Test rejecting path traversal attempts."""
        allowed_dir = tmp_path / "output"
        allowed_dir.mkdir()

        malicious_paths = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "../../../sensitive.txt",
            "test/../../etc/passwd",
        ]

        for path in malicious_paths:
            with pytest.raises(ValueError, match="Path traversal"):
                sanitize_file_path(path, allowed_dir)

    def test_sanitize_absolute_path(self, tmp_path):
        """Test handling absolute paths."""
        allowed_dir = tmp_path / "output"
        allowed_dir.mkdir()

        # Absolute path outside allowed directory should be rejected
        with pytest.raises(ValueError, match="outside allowed"):
            sanitize_file_path("/etc/passwd", allowed_dir)

    def test_sanitize_nested_valid_path(self, tmp_path):
        """Test sanitizing nested valid path."""
        allowed_dir = tmp_path / "output"
        (allowed_dir / "subdir").mkdir(parents=True)

        result = sanitize_file_path("subdir/test.mp3", allowed_dir)
        assert result == (allowed_dir / "subdir" / "test.mp3").resolve()


class TestVoiceNameValidation:
    """Test voice name validation."""

    def test_validate_valid_voice_by_name(self):
        """Test validating valid voice by display name."""
        allowed_voices = {
            "晓晓-女声": "zh-CN-XiaoxiaoNeural",
            "云扬-男声": "zh-CN-YunyangNeural",
        }

        assert validate_voice_name("晓晓-女声", allowed_voices) is True
        assert validate_voice_name("云扬-男声", allowed_voices) is True

    def test_validate_valid_voice_by_id(self):
        """Test validating valid voice by ID."""
        allowed_voices = {
            "晓晓-女声": "zh-CN-XiaoxiaoNeural",
            "云扬-男声": "zh-CN-YunyangNeural",
        }

        assert validate_voice_name("zh-CN-XiaoxiaoNeural", allowed_voices) is True

    def test_validate_invalid_voice(self):
        """Test rejecting invalid voice."""
        allowed_voices = {
            "晓晓-女声": "zh-CN-XiaoxiaoNeural",
        }

        assert validate_voice_name("InvalidVoice", allowed_voices) is False
        assert validate_voice_name("zh-CN-InvalidNeural", allowed_voices) is False

    def test_validate_empty_allowed_voices(self):
        """Test with empty allowed voices."""
        allowed_voices = {}

        assert validate_voice_name("AnyVoice", allowed_voices) is False


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_valid_filename(self):
        """Test sanitizing valid filename."""
        result = sanitize_filename("test_audio.mp3")
        assert result == "test_audio.mp3"

    def test_sanitize_filename_with_path(self):
        """Test removing path from filename."""
        result = sanitize_filename("../../etc/passwd")
        assert result == "passwd"
        assert ".." not in result

    def test_sanitize_filename_with_dangerous_chars(self):
        """Test removing dangerous characters."""
        test_cases = [
            ("test<>file.mp3", "test__file.mp3"),
            ('file:name.mp3', "file_name.mp3"),
            ("file?name*.mp3", "file_name_.mp3"),
            ('file|name.mp3', "file_name.mp3"),
            ('file"name.mp3', "file_name.mp3"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_sanitize_long_filename(self):
        """Test truncating long filename."""
        # Create a filename longer than 255 chars
        long_name = "a" * 300 + ".mp3"
        result = sanitize_filename(long_name)

        assert len(result) <= 255
        assert result.endswith(".mp3")

    def test_sanitize_filename_with_extension(self):
        """Test preserving file extension."""
        result = sanitize_filename("test_audio_file.mp3")
        assert result.endswith(".mp3")
        assert "test_audio_file" in result
