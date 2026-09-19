"""FastAPI dependencies for database sessions and authentication."""

import uuid
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import SessionLocal, get_db
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, UnauthorizedAccessError
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validates JWT access token and returns authenticated User."""
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Could not validate credentials.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token.")

    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found.")
    if not user.is_active:
        raise UnauthorizedAccessError("User account is inactive.")

    return user
