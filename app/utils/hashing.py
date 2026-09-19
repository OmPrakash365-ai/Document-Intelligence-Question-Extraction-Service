"""File and content hashing utilities."""

import hashlib
from typing import BinaryIO


def calculate_sha256(data: bytes) -> str:
    """Calculates the SHA-256 hash of a byte string."""
    return hashlib.sha256(data).hexdigest()


def calculate_stream_sha256(file_obj: BinaryIO, chunk_size: int = 65536) -> str:
    """Calculates the SHA-256 hash of a file stream without loading the entire file into memory."""
    hasher = hashlib.sha256()
    pos = file_obj.tell()
    file_obj.seek(0)
    while chunk := file_obj.read(chunk_size):
        hasher.update(chunk)
    file_obj.seek(pos)
    return hasher.hexdigest()
