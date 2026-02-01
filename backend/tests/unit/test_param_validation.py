"""Unit tests for parameter validation.

Tests validation of voice parameters in TaskCreateRequest schema.
"""

import pytest
from pydantic import ValidationError

from src.api.schemas import TaskCreateRequest


class TestRateValidation:
    """Test speech rate parameter validation."""

    def test_valid_rate(self):
        """Test valid rate values."""
        request = TaskCreateRequest(text="Hello", rate=1.0)
        assert request.rate == 1.0

        request = TaskCreateRequest(text="Hello", rate=0.5)
        assert request.rate == 0.5

        request = TaskCreateRequest(text="Hello", rate=2.0)
        assert request.rate == 2.0

    def test_rate_default(self):
        """Test default rate value."""
        request = TaskCreateRequest(text="Hello")
        assert request.rate == 1.0

    def test_rate_below_minimum(self):
        """Test rate below minimum (0.5)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", rate=0.4)

        errors = exc_info.value.errors()
        assert any("rate" in str(err).lower() for err in errors)

    def test_rate_above_maximum(self):
        """Test rate above maximum (2.0)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", rate=2.1)

        errors = exc_info.value.errors()
        assert any("rate" in str(err).lower() for err in errors)

    def test_rate_boundary_values(self):
        """Test rate at boundary values."""
        # Minimum boundary
        request = TaskCreateRequest(text="Hello", rate=0.5)
        assert request.rate == 0.5

        # Maximum boundary
        request = TaskCreateRequest(text="Hello", rate=2.0)
        assert request.rate == 2.0

    def test_rate_type_error(self):
        """Test rate with wrong type."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(text="Hello", rate="invalid")


class TestPitchValidation:
    """Test pitch parameter validation."""

    def test_valid_pitch(self):
        """Test valid pitch values."""
        request = TaskCreateRequest(text="Hello", pitch=1.0)
        assert request.pitch == 1.0

        request = TaskCreateRequest(text="Hello", pitch=0.5)
        assert request.pitch == 0.5

        request = TaskCreateRequest(text="Hello", pitch=2.0)
        assert request.pitch == 2.0

    def test_pitch_default(self):
        """Test default pitch value."""
        request = TaskCreateRequest(text="Hello")
        assert request.pitch == 1.0

    def test_pitch_below_minimum(self):
        """Test pitch below minimum (0.5)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", pitch=0.4)

        errors = exc_info.value.errors()
        assert any("pitch" in str(err).lower() for err in errors)

    def test_pitch_above_maximum(self):
        """Test pitch above maximum (2.0)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", pitch=2.1)

        errors = exc_info.value.errors()
        assert any("pitch" in str(err).lower() for err in errors)

    def test_pitch_boundary_values(self):
        """Test pitch at boundary values."""
        # Minimum boundary
        request = TaskCreateRequest(text="Hello", pitch=0.5)
        assert request.pitch == 0.5

        # Maximum boundary
        request = TaskCreateRequest(text="Hello", pitch=2.0)
        assert request.pitch == 2.0


class TestVolumeValidation:
    """Test volume parameter validation."""

    def test_valid_volume(self):
        """Test valid volume values."""
        request = TaskCreateRequest(text="Hello", volume=1.0)
        assert request.volume == 1.0

        request = TaskCreateRequest(text="Hello", volume=0.5)
        assert request.volume == 0.5

        request = TaskCreateRequest(text="Hello", volume=0.0)
        assert request.volume == 0.0

    def test_volume_default(self):
        """Test default volume value."""
        request = TaskCreateRequest(text="Hello")
        assert request.volume == 1.0

    def test_volume_below_minimum(self):
        """Test volume below minimum (0.0)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", volume=-0.1)

        errors = exc_info.value.errors()
        assert any("volume" in str(err).lower() for err in errors)

    def test_volume_above_maximum(self):
        """Test volume above maximum (1.0)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", volume=1.1)

        errors = exc_info.value.errors()
        assert any("volume" in str(err).lower() for err in errors)

    def test_volume_boundary_values(self):
        """Test volume at boundary values."""
        # Minimum boundary
        request = TaskCreateRequest(text="Hello", volume=0.0)
        assert request.volume == 0.0

        # Maximum boundary
        request = TaskCreateRequest(text="Hello", volume=1.0)
        assert request.volume == 1.0


class TestVoiceValidation:
    """Test voice name parameter validation."""

    def test_valid_voice_by_name(self):
        """Test valid voice by Chinese name."""
        request = TaskCreateRequest(text="Hello", voice_name="晓晓-女声")
        assert request.voice_name == "zh-CN-XiaoxiaoNeural"

    def test_valid_voice_by_id(self):
        """Test valid voice by ID."""
        request = TaskCreateRequest(text="Hello", voice_name="zh-CN-XiaoxiaoNeural")
        assert request.voice_name == "zh-CN-XiaoxiaoNeural"

    def test_voice_default(self):
        """Test default voice value."""
        request = TaskCreateRequest(text="Hello")
        assert request.voice_name == "zh-CN-XiaoxiaoNeural"

    def test_invalid_voice(self):
        """Test invalid voice name."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(text="Hello", voice_name="invalid-voice")

        errors = exc_info.value.errors()
        assert any("voice" in str(err).lower() for err in errors)

    def test_all_preset_voices(self):
        """Test all preset voices are valid."""
        preset_voices = [
            ("晓晓-女声", "zh-CN-XiaoxiaoNeural"),
            ("云扬-男声", "zh-CN-YunyangNeural"),
            ("晓悠-童声", "zh-CN-XiaoyouNeural"),
            ("晓伊-年轻女声", "zh-CN-XiaoyiNeural"),
            ("云健-沉稳男声", "zh-CN-YunjianNeural"),
        ]

        for name, voice_id in preset_voices:
            # Test by name
            request = TaskCreateRequest(text="Hello", voice_name=name)
            assert request.voice_name == voice_id

            # Test by ID
            request = TaskCreateRequest(text="Hello", voice_name=voice_id)
            assert request.voice_name == voice_id


class TestCombinedParameters:
    """Test multiple parameters combined."""

    def test_all_parameters_valid(self):
        """Test all parameters are valid."""
        request = TaskCreateRequest(
            text="Hello world",
            voice_name="云扬-男声",
            rate=1.5,
            pitch=1.2,
            volume=0.8,
        )

        assert request.text == "Hello world"
        assert request.voice_name == "zh-CN-YunyangNeural"
        assert request.rate == 1.5
        assert request.pitch == 1.2
        assert request.volume == 0.8

    def test_all_defaults(self):
        """Test all parameters use defaults."""
        request = TaskCreateRequest(text="Hello")

        assert request.text == "Hello"
        assert request.voice_name == "zh-CN-XiaoxiaoNeural"
        assert request.rate == 1.0
        assert request.pitch == 1.0
        assert request.volume == 1.0

    def test_multiple_invalid_parameters(self):
        """Test validation with multiple invalid parameters."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(
                text="Hello",
                rate=3.0,  # Invalid
                pitch=0.3,  # Invalid
                volume=1.5,  # Invalid
                voice_name="invalid",  # Invalid
            )

        errors = exc_info.value.errors()
        # Should have errors for rate, pitch, volume, and voice_name
        assert len(errors) >= 3


class TestTextValidation:
    """Test text validation with parameters."""

    def test_text_with_parameters(self):
        """Test text validation works with parameters."""
        request = TaskCreateRequest(
            text="  Hello world  ",  # Has whitespace
            rate=1.5,
            pitch=1.2,
            volume=0.8,
        )

        # Text should be stripped
        assert request.text == "Hello world"
        # Parameters should be preserved
        assert request.rate == 1.5
        assert request.pitch == 1.2
        assert request.volume == 0.8

    def test_null_bytes_in_text(self):
        """Test null bytes are rejected."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(
                text="Hello\x00world",
                rate=1.0,
            )
