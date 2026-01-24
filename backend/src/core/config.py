"""
Application configuration management.

Uses pydantic-settings for environment-based configuration.
"""
import os
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
