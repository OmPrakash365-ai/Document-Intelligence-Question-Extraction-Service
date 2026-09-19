"""Schemas package."""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentPageResponse,
    DocumentRelationCreate,
    DocumentRelationResponse,
)
from app.schemas.question import (
    OptionItem,
    QuestionAnswer,
    QuestionSource,
    QuestionResponse,
    QuestionListResponse,
)
from app.schemas.answer import AnswerResponse
from app.schemas.review import ReviewItemResponse, ReviewItemListResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "DocumentUploadResponse",
    "DocumentStatusResponse",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentPageResponse",
    "DocumentRelationCreate",
    "DocumentRelationResponse",
    "OptionItem",
    "QuestionAnswer",
    "QuestionSource",
    "QuestionResponse",
    "QuestionListResponse",
    "AnswerResponse",
    "ReviewItemResponse",
    "ReviewItemListResponse",
]
