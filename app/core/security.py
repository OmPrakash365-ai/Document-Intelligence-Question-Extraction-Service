"""Security utilities: password hashing, JWT tokens, and path traversal protection."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union
import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its bcrypt hash."""
    try:
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for a plain password."""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Creates a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if "sub" not in payload:
            raise AuthenticationError("Invalid token subject.")
        return payload
    except JWTError as exc:
        raise AuthenticationError(f"Invalid or expired token: {str(exc)}")


def safe_join(base_directory: Union[str, Path], *paths: str) -> Path:
    """
    Safely joins paths ensuring that the resolved destination remains inside base_directory.
    Prevents directory traversal attacks.
    """
    base = Path(base_directory).resolve()
    target = (base / Path(*paths)).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {target} is outside {base}")

    return target
