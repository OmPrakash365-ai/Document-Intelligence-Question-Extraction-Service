"""Unit tests for security functions."""

import pytest
from pathlib import Path
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    safe_join,
)
from app.core.exceptions import AuthenticationError


def test_password_hashing():
    plain = "MySecretPassword123!"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token():
    subject = "user-12345"
    token = create_access_token(subject=subject)
    payload = decode_access_token(token)
    assert payload["sub"] == subject

    # Invalid token
    with pytest.raises(AuthenticationError):
        decode_access_token("invalid.token.structure")


def test_safe_join():
    base_dir = Path("/tmp/safe_storage")
    joined = safe_join(base_dir, "subfolder", "file.pdf")
    assert str(joined).startswith(str(base_dir.resolve()))

    # Traversal attempt
    with pytest.raises(ValueError):
        safe_join(base_dir, "../../etc/passwd")
