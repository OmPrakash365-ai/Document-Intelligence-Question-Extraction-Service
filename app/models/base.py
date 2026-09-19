"""Base model and mixins."""

import uuid
from app.core.database import Base, GUID, TimestampMixin

__all__ = ["Base", "GUID", "TimestampMixin", "uuid"]
