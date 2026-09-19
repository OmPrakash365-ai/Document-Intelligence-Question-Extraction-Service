"""Unit tests for file validation and security utilities."""

import pytest
from app.utils.file_validation import (
    validate_file_extension,
    validate_file_size,
    validate_file_content,
    generate_secure_storage_filename,
)
from app.core.exceptions import (
    UnsupportedFileTypeError,
    FileSizeExceededError,
    MalformedFileError,
)


def test_validate_file_extension():
    assert validate_file_extension("document.pdf") == "pdf"
    assert validate_file_extension("image.PNG") == "png"
    assert validate_file_extension("test.file.jpeg") == "jpeg"
    assert validate_file_extension("photo.jpg") == "jpg"

    with pytest.raises(UnsupportedFileTypeError):
        validate_file_extension("script.exe")

    with pytest.raises(UnsupportedFileTypeError):
        validate_file_extension("document.txt")

    with pytest.raises(UnsupportedFileTypeError):
        validate_file_extension("no_extension")


def test_validate_file_size():
    # Valid size (1MB)
    validate_file_size(1024 * 1024)

    # Empty file
    with pytest.raises(MalformedFileError):
        validate_file_size(0)

    # Exceeding size (>25MB)
    with pytest.raises(FileSizeExceededError):
        validate_file_size(26 * 1024 * 1024)


def test_validate_file_content():
    # Valid PDF magic bytes
    validate_file_content(b"%PDF-1.4 header bytes", "pdf")

    # Valid JPEG magic bytes
    validate_file_content(b"\xff\xd8\xff\xe0\x00\x10JFIF", "jpeg")
    validate_file_content(b"\xff\xd8\xff\xe0\x00\x10JFIF", "jpg")

    # Valid PNG magic bytes
    validate_file_content(b"\x89PNG\r\n\x1a\n\x00\x00", "png")

    # Malformed PDF (disguised text file)
    with pytest.raises(MalformedFileError):
        validate_file_content(b"Hello world, I am a text file", "pdf")


def test_generate_secure_storage_filename():
    sec_name, ext = generate_secure_storage_filename("my_exam_final_2026.pdf")
    assert ext == "pdf"
    assert sec_name.endswith(".pdf")
    assert "my_exam_final_2026" not in sec_name
    assert len(sec_name) > 30  # UUID hex length + .pdf
