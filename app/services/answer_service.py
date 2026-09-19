"""Answer service for retrieving question answers."""

import uuid
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AnswerNotFoundError,
    QuestionNotFoundError,
    UnauthorizedAccessError,
)
from app.models.user import User
from app.repositories.answer_repository import AnswerRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.answer import AnswerResponse


class AnswerService:
    def __init__(self, db: Session):
        self.db = db
        self.answer_repo = AnswerRepository(db)
        self.question_repo = QuestionRepository(db)
        self.doc_repo = DocumentRepository(db)

    def get_answer_for_question(
        self, question_id: uuid.UUID, current_user: User
    ) -> AnswerResponse:
        q = self.question_repo.get_by_id(question_id)
        if not q:
            raise QuestionNotFoundError(str(question_id))

        doc = self.doc_repo.get_by_id(q.document_id)
        if not doc or doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("You do not have permission to view this answer.")

        ans = self.answer_repo.get_by_question_id(question_id)
        if not ans:
            raise AnswerNotFoundError(str(question_id))

        return AnswerResponse(
            id=ans.id,
            question_id=ans.question_id,
            value=ans.answer_value,
            answer_type=ans.answer_type,
            confidence=ans.confidence,
            matching_status=ans.matching_status,
            source_document_id=ans.source_document_id,
            source_page=ans.source_page,
        )
