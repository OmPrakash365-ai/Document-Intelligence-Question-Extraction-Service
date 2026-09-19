"""API routes package."""

from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.questions import router as questions_router
from app.api.routes.answers import router as answers_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.health import router as health_router

__all__ = [
    "auth_router",
    "documents_router",
    "questions_router",
    "answers_router",
    "reviews_router",
    "health_router",
]
