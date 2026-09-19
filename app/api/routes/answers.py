"""Answer API routes."""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.answer import AnswerResponse
from app.services.answer_service import AnswerService

router = APIRouter(tags=["Answers"])


@router.get(
    "/questions/{question_id}/answer",
    response_model=AnswerResponse,
    summary="Get answer for question",
    description="Returns the extracted answer information associated with a question, including confidence and matching status.",
)
def get_question_answer(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerResponse:
    service = AnswerService(db)
    return service.get_answer_for_question(
        question_id=question_id, current_user=current_user
    )
