"""
Application configuration management.

Uses pydantic-settings for environment-based configuration.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/tts_history.db"

    # Application
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    MAX_QUEUE_SIZE: int = 10
    MAX_HISTORY_SIZE: int = 20

    # Paths
    OUTPUT_DIR: Path = Field(default_factory=lambda: Path("output"))
    LOG_DIR: Path = Field(default_factory=lambda: Path("logs"))

    # TTS Engine
    DEFAULT_VOICE: str = "zh-CN-XiaoxiaoNeural"
    AUDIO_BITRATE: int = 128000  # 128kbps
    AUDIO_SAMPLE_RATE: int = 44100

    # Voice Presets
    PRESET_VOICES: dict[str, str] = {
        "晓晓-女声": "zh-CN-XiaoxiaoNeural",
        "云扬-男声": "zh-CN-YunyangNeural",
        "晓悠-童声": "zh-CN-XiaoyouNeural",
        "晓伊-年轻女声": "zh-CN-XiaoyiNeural",
        "云健-沉稳男声": "zh-CN-YunjianNeural",
    }

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()


# ==================== Voice Helper Functions ====================


def get_voice_name(voice_id: str) -> str | None:
    """Get voice display name from voice ID.

    Args:
        voice_id: Voice ID (e.g., "zh-CN-XiaoxiaoNeural")

    Returns:
        Display name (e.g., "晓晓-女声") or None if not found
    """
    for name, vid in settings.PRESET_VOICES.items():
        if vid == voice_id:
            return name
    return None


def get_voice_id(voice_name: str) -> str | None:
    """Get voice ID from display name or ID.

    Args:
        voice_name: Display name (e.g., "晓晓-女声") or voice ID

    Returns:
        Voice ID or None if not found
    """
    # Direct ID lookup
    if voice_name in settings.PRESET_VOICES.values():
        return voice_name

    # Name lookup
    return settings.PRESET_VOICES.get(voice_name)


def get_all_voices() -> dict[str, str]:
    """Get all available voices.

    Returns:
        Dictionary mapping display names to voice IDs
    """
    return settings.PRESET_VOICES.copy()


def validate_voice(voice_name: str) -> bool:
    """Validate if voice name or ID is available.

    Args:
        voice_name: Display name or voice ID

    Returns:
        True if voice is available, False otherwise
    """
    return (
        voice_name in settings.PRESET_VOICES
        or voice_name in settings.PRESET_VOICES.values()
    )
