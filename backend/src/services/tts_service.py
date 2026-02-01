"""TTS service for audio generation.

Handles interaction with edge-tts engine for text-to-speech conversion.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

import edge_tts

from src.core.config import settings
from src.core.logger import get_logger
from src.models.task import Task, TaskStatus

# Get logger with context
log = get_logger("TTSService")


class TTSService:
    """Service for TTS audio generation using edge-tts."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize TTS service.

        Args:
            output_dir: Directory for output audio files (default: from settings)
        """
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_audio(
        self,
        task: Task,
        progress_callback: callable | None = None,
    ) -> str:
        """Generate audio file from text using edge-tts.

        Args:
            task: Task object with text and voice parameters
            progress_callback: Optional callback for progress updates

        Returns:
            Path to generated audio file

        Raises:
            Exception: If TTS generation fails
        """
        task_id = task.task_id
        text_length = len(task.text)

        log.info(
            f"Task lifecycle: START - task_id={task_id}, "
            f"text_length={text_length}, voice={task.voice_name}, "
            f"rate={task.rate}, pitch={task.pitch}, volume={task.volume}"
        )

        try:
            # Update task status
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            task.progress = 0

            log.debug(f"Task lifecycle: PROCESSING - task_id={task_id}")

            if progress_callback:
                await progress_callback(10)

            # Create communicate object with safe parameter handling
            rate = task.rate if task.rate is not None else 1.0
            pitch = task.pitch if task.pitch is not None else 1.0
            volume = task.volume if task.volume is not None else 1.0

            log.debug(
                f"Task {task_id}: Using TTS parameters - rate={rate}, pitch={pitch}, volume={volume}"
            )

            communicate = edge_tts.Communicate(
                text=task.text,
                voice=task.voice_name,
                rate=(
                    f"+{int((rate - 1) * 100)}%"
                    if rate >= 1
                    else f"{int((rate - 1) * 100)}%"
                ),
                pitch=(
                    f"+{int((pitch - 1) * 100)}Hz"
                    if pitch >= 1
                    else f"{int((pitch - 1) * 100)}Hz"
                ),
                volume=(
                    f"+{int((volume - 1) * 100)}%"
                    if volume >= 1
                    else f"{int((volume - 1) * 100)}%"
                ),
            )

            # Generate output file path
            # Use custom filename if provided, otherwise use task_id
            if task.custom_filename:
                # Log original filename for debugging
                log.debug(
                    f"Task {task_id}: Original custom_filename: {repr(task.custom_filename)}"
                )

                # Sanitize custom filename - remove invalid characters
                import re
                # Remove newlines, tabs, and special characters
                safe_filename = task.custom_filename.strip()
                # Remove newlines, tabs, and replace with space
                safe_filename = safe_filename.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                # Remove multiple spaces
                safe_filename = re.sub(r'\s+', ' ', safe_filename)
                # Remove any file extension if present
                if '.' in safe_filename:
                    safe_filename = safe_filename.rsplit('.', 1)[0]
                # Remove special characters (keep only alphanumeric, Chinese, and basic symbols)
                safe_filename = re.sub(r'[^\w\s\u4e00-\u9fff\-_.]', '', safe_filename)
                # Remove leading/trailing spaces and dots
                safe_filename = safe_filename.strip().strip('.')
                # Limit length
                if len(safe_filename) > 200:
                    safe_filename = safe_filename[:200]

                log.debug(
                    f"Task {task_id}: Sanitized filename: {repr(safe_filename)}"
                )

                if safe_filename:
                    output_filename = f"{safe_filename}.mp3"
                else:
                    log.warning(
                        f"Task {task_id}: Sanitization resulted in empty string, using task_id"
                    )
                    output_filename = f"{task.task_id}.mp3"
            else:
                output_filename = f"{task.task_id}.mp3"
            output_path = self.output_dir / output_filename

            log.debug(f"Task {task_id}: Generating audio to {output_path}")

            if progress_callback:
                await progress_callback(30)

            # Save audio to file
            await communicate.save(str(output_path))

            log.debug(f"Task {task_id}: Audio generation complete, verifying file")

            if progress_callback:
                await progress_callback(90)

            # Verify file was created
            if not output_path.exists():
                log.error(f"Task {task_id}: Audio file was not created")
                raise Exception("Audio file was not created")

            file_size = output_path.stat().st_size
            log.info(
                f"Task lifecycle: SUCCESS - task_id={task_id}, file_size={file_size} bytes"
            )

            # Update task
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.completed_at = datetime.now()
            task.file_path = str(output_path)
            # Store filename without extension for frontend use
            task.filename = output_path.stem  # filename without .mp3 extension

            if progress_callback:
                await progress_callback(100)

            return str(output_path)

        except Exception as e:
            log.exception(f"Task lifecycle: FAILED - task_id={task_id}, error={str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            raise

    async def generate_audio_simple(
        self,
        text: str,
        voice_name: str = "zh-CN-XiaoxiaoNeural",
        rate: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
    ) -> tuple[str, str]:
        """Generate audio without task tracking (simple version).

        Args:
            text: Text to convert
            voice_name: Voice name
            rate: Speech rate
            pitch: Pitch multiplier
            volume: Volume level

        Returns:
            Tuple of (task_id, file_path)

        Raises:
            Exception: If generation fails
        """
        # Generate task ID
        task_id = str(uuid.uuid4())

        # Create temporary task object
        task = Task(
            task_id=task_id,
            text=text,
            voice_name=voice_name,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        # Generate audio
        file_path = await self.generate_audio(task)

        return task_id, file_path

    def get_audio_file_path(self, task_id: str) -> Path:
        """Get audio file path for a task.

        Args:
            task_id: Task identifier

        Returns:
            Path to audio file
        """
        return self.output_dir / f"{task_id}.mp3"

    def audio_file_exists(self, task_id: str) -> bool:
        """Check if audio file exists for task.

        Args:
            task_id: Task identifier

        Returns:
            True if file exists
        """
        return self.get_audio_file_path(task_id).exists()

    def delete_audio_file(self, task_id: str) -> bool:
        """Delete audio file for task.

        Args:
            task_id: Task identifier

        Returns:
            True if file was deleted
        """
        try:
            file_path = self.get_audio_file_path(task_id)
            if file_path.exists():
                file_path.unlink()
                log.info(f"Deleted audio file: {file_path}")
                return True
            return False
        except Exception as e:
            log.error(f"Failed to delete audio file for task {task_id}: {e}")
            return False
