"""Pydantic schemas for API requests and responses.

Defines request and response models for TTS API endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==================== Task Schemas ====================


class TaskCreateRequest(BaseModel):
    """Request schema for creating a new TTS task."""

    text: str = Field(
        ..., min_length=1, max_length=5000, description="Text to convert to speech"
    )
    voice_name: str = Field(
        default="zh-CN-XiaoxiaoNeural",
        description="Voice name for TTS",
    )
    rate: float = Field(
        default=1.0, ge=0.5, le=2.0, description="Speech rate multiplier"
    )
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Pitch multiplier")
    volume: float = Field(default=1.0, ge=0.0, le=1.0, description="Volume level")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text input.

        Args:
            v: Text value to validate

        Returns:
            Validated text

        Raises:
            ValueError: If text contains invalid characters
        """
        # Check for null bytes
        if "\x00" in v:
            raise ValueError("Text cannot contain null bytes")

        # Strip leading/trailing whitespace but preserve internal whitespace
        return v.strip()

    @field_validator("voice_name")
    @classmethod
    def validate_voice(cls, v: str) -> str:
        """Validate voice name.

        Args:
            v: Voice name value to validate

        Returns:
            Validated voice ID

        Raises:
            ValueError: If voice name is not allowed
        """
        return validate_voice_name(v)


class TaskResponse(BaseModel):
    """Response schema for task information."""

    task_id: str
    text: str
    voice_name: str
    rate: float
    pitch: float
    volume: float
    status: str
    progress: int
    file_path: str | None = None
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Response schema for list of tasks."""

    tasks: list[TaskResponse]
    total: int


# ==================== History Schemas ====================


class HistoryResponse(BaseModel):
    """Response schema for history record."""

    id: int
    task_id: str
    text_summary: str
    voice_params: str
    created_at: str
    file_path: str
    file_size: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class HistoryListResponse(BaseModel):
    """Response schema for list of history records."""

    records: list[HistoryResponse]
    total: int


# ==================== Queue Schemas ====================


class QueueStatusResponse(BaseModel):
    """Response schema for queue status."""

    queued_count: int
    processing_count: int
    completed_count: int
    current_task: TaskResponse | None = None
    max_queue_size: int


# ==================== Voice Schemas ====================


class VoiceInfo(BaseModel):
    """Information about a voice."""

    name: str
    voice_id: str
    description: str
    default: bool


class VoicesResponse(BaseModel):
    """Response schema for available voices."""

    voices: list[VoiceInfo]


# ==================== Error Schemas ====================


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict | None = Field(None, description="Additional error details")


# ==================== Validation ====================


PRESET_VOICES = {
    "晓晓-女声": "zh-CN-XiaoxiaoNeural",
    "云扬-男声": "zh-CN-YunyangNeural",
    "晓悠-童声": "zh-CN-XiaoyouNeural",
    "晓伊-年轻女声": "zh-CN-XiaoyiNeural",
    "云健-沉稳男声": "zh-CN-YunjianNeural",
}


def validate_voice_name(voice_name: str) -> str:
    """Validate voice name against allowed list.

    Args:
        voice_name: Voice name to validate (can be Chinese name or voice ID)

    Returns:
        Validated voice ID (e.g., "zh-CN-XiaoxiaoNeural")

    Raises:
        ValueError: If voice name is not allowed
    """
    # Check if it's a preset key (Chinese name) -> return voice ID
    if voice_name in PRESET_VOICES:
        return PRESET_VOICES[voice_name]

    # Check if it's already a valid voice ID
    if voice_name in PRESET_VOICES.values():
        return voice_name

    raise ValueError(
        f"Invalid voice name. Allowed voices: {', '.join(PRESET_VOICES.keys())}"
    )
