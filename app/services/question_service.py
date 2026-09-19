"""Question service for retrieving extracted questions and details."""

import uuid
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import (
    QuestionNotFoundError,
    UnauthorizedAccessError,
    DocumentNotFoundError,
)
from app.models.user import User
from app.models.question import Question
from app.models.document import Document
from app.repositories.question_repository import QuestionRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.question import (
    QuestionResponse,
    OptionItem,
    QuestionAnswer,
    QuestionSource,
)


class QuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repo = QuestionRepository(db)
        self.doc_repo = DocumentRepository(db)

    def _to_response_schema(self, q: Question) -> QuestionResponse:
        """Maps a Question ORM model to the Section 17 response schema."""
        options = [
            OptionItem(key=opt.option_key, text=opt.option_text, confidence=opt.confidence)
            for opt in q.options
        ]

        answer = None
        if q.answer:
            answer = QuestionAnswer(
                value=q.answer.answer_value,
                confidence=q.answer.confidence,
                matching_status=q.answer.matching_status,
                source_document_id=q.answer.source_document_id,
                source_page=q.answer.source_page,
            )

        pages = list(range(q.source_start_page, q.source_end_page + 1))

        return QuestionResponse(
            id=q.id,
            document_id=q.document_id,
            question_number=q.question_number,
            question=q.question_text,
            question_type=q.question_type,
            options=options,
            answer=answer,
            source=QuestionSource(document_id=q.document_id, pages=pages),
            confidence=q.confidence,
            extraction_status=q.extraction_status,
        )

    def list_questions(
        self,
        document_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        size: int = 50,
    ) -> Tuple[List[QuestionResponse], int]:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        if doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("You do not have permission to view these questions.")

        questions, total = self.question_repo.list_by_document(
            document_id=document_id, page=page, size=size
        )
        responses = [self._to_response_schema(q) for q in questions]
        return responses, total

    def get_question(
        self, question_id: uuid.UUID, current_user: User
    ) -> QuestionResponse:
        q = self.question_repo.get_by_id(question_id)
        if not q:
            raise QuestionNotFoundError(str(question_id))

        doc = self.doc_repo.get_by_id(q.document_id)
        if not doc or doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("You do not have permission to view this question.")

        return self._to_response_schema(q)
