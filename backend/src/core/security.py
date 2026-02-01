"""
Security and input validation utilities.

Provides input sanitization and security checks.
"""

import os
import re
from pathlib import Path

# Patterns for security validation
PATH_TRAVERSAL_PATTERN = re.compile(r"\.\.[/\\]")
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")
COMMAND_INJECTION_CHARS = set(";|&`$()<>")

MAX_TEXT_LENGTH = 5000


def sanitize_text(text: str) -> str:
    """
    Sanitize user input text.

    Args:
        text: User input text

    Returns:
        Sanitized text

    Raises:
        ValueError: If text contains malicious patterns
    """
    # Remove null bytes first
    text = text.replace("\x00", "")

    # Check for path traversal attempts
    if PATH_TRAVERSAL_PATTERN.search(text):
        raise ValueError("Text contains path traversal patterns")

    # Check for control characters (except newline, tab, carriage return)
    # Allow: \n (0x0A), \r (0x0D), \t (0x09)
    control_chars_without_allowed = CONTROL_CHARS_PATTERN.pattern.replace(
        r"[\x00-\x1f\x7f-\x9f]", r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"
    )
    if re.search(control_chars_without_allowed, text):
        raise ValueError("Text contains invalid control characters")

    return text


def validate_text_length(text: str) -> bool:
    """
    Validate text length.

    Args:
        text: Text to validate

    Returns:
        True if length is valid
    """
    return 0 < len(text) <= MAX_TEXT_LENGTH


def sanitize_file_path(file_path: str, allowed_dir: Path) -> Path:
    """
    Sanitize and validate file path.

    Args:
        file_path: File path to validate
        allowed_dir: Directory where file operations are allowed

    Returns:
        Absolute, sanitized Path object

    Raises:
        ValueError: If path tries to escape allowed directory
    """
    # Resolve to absolute path
    resolved_path = (allowed_dir / file_path).resolve()

    # Ensure resolved path is within allowed directory
    try:
        resolved_path.relative_to(allowed_dir.resolve())
    except ValueError:
        raise ValueError(
            f"Path traversal detected: {file_path} is outside allowed directory {allowed_dir}"
        )

    return resolved_path


def validate_voice_name(voice_name: str, allowed_voices: dict) -> bool:
    """
    Validate voice name against allowed list.

    Args:
        voice_name: Voice name to validate (can be display name or voice ID)
        allowed_voices: Dictionary of allowed voices (display name -> voice ID)

    Returns:
        True if voice is valid
    """
    # Check if it's a valid display name (key)
    if voice_name in allowed_voices:
        return True

    # Check if it's a valid voice ID (value)
    if voice_name in allowed_voices.values():
        return True

    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext

    return filename
