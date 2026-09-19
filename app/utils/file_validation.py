"""File validation utilities for secure uploads."""

import os
import uuid
from typing import Tuple
from app.core.config import get_settings
from app.core.exceptions import (
    UnsupportedFileTypeError,
    FileSizeExceededError,
    MalformedFileError,
)

settings = get_settings()

# Magic bytes signatures for supported formats
MAGIC_SIGNATURES = {
    "pdf": [b"%PDF"],
    "jpeg": [b"\xff\xd8\xff"],
    "jpg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG\r\n\x1a\n"],
}


def validate_file_extension(filename: str) -> str:
    """Validates and returns normalized lowercase file extension without leading dot."""
    if not filename or "." not in filename:
        raise UnsupportedFileTypeError("Filename has no valid extension.")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"File extension '.{ext}' is not supported. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext


def validate_file_size(size_in_bytes: int) -> None:
    """Validates file size against maximum configured upload limit."""
    if size_in_bytes <= 0:
        raise MalformedFileError("Uploaded file is empty.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_in_bytes > max_bytes:
        raise FileSizeExceededError(settings.MAX_UPLOAD_SIZE_MB)


def validate_file_content(header_bytes: bytes, ext: str) -> None:
    """Validates file content using magic byte signatures to prevent file disguise attacks."""
    signatures = MAGIC_SIGNATURES.get(ext, [])
    if not signatures:
        raise UnsupportedFileTypeError(f"Unsupported extension: {ext}")

    matches = any(header_bytes.startswith(sig) for sig in signatures)
    if not matches:
        raise MalformedFileError(
            f"File content does not match the expected signature for '.{ext}'"
        )


def generate_secure_storage_filename(original_filename: str) -> Tuple[str, str]:
    """
    Generates a cryptographically random filename for storage to prevent
    path traversal, name collisions, and arbitrary execution.
    Returns (secure_filename, extension).
    """
    ext = validate_file_extension(original_filename)
    secure_filename = f"{uuid.uuid4().hex}.{ext}"
    return secure_filename, ext
