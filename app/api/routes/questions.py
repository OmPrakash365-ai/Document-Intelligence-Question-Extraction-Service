"""Question API routes."""

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.question import QuestionResponse, QuestionListResponse
from app.services.question_service import QuestionService

router = APIRouter(tags=["Questions"])


@router.get(
    "/documents/{document_id}/questions",
    response_model=QuestionListResponse,
    summary="Get questions for document",
    description="Returns a paginated list of structured questions extracted from a document.",
)
def list_questions(
    document_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionListResponse:
    service = QuestionService(db)
    items, total = service.list_questions(
        document_id=document_id, current_user=current_user, page=page, size=size
    )
    pages = (total + size - 1) // size if total > 0 else 0
    return QuestionListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Get question by ID",
    description="Retrieves a single extracted question with its options, answer, source pages, and confidence score.",
)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    service = QuestionService(db)
    return service.get_question(question_id=question_id, current_user=current_user)
