"""Answer repository."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer


class AnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_question_id(self, question_id: uuid.UUID) -> Optional[Answer]:
        stmt = select(Answer).where(Answer.question_id == question_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, answer_id: uuid.UUID) -> Optional[Answer]:
        stmt = select(Answer).where(Answer.id == answer_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_answer(self, answer: Answer) -> Answer:
        existing = self.get_by_question_id(answer.question_id)
        if existing:
            existing.answer_value = answer.answer_value
            existing.answer_type = answer.answer_type
            existing.confidence = answer.confidence
            existing.source_document_id = answer.source_document_id
            existing.source_page = answer.source_page
            existing.matching_status = answer.matching_status
            self.db.commit()
            self.db.refresh(existing)
            return existing

        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def list_by_source_document(
        self, source_document_id: uuid.UUID
    ) -> List[Answer]:
        stmt = select(Answer).where(Answer.source_document_id == source_document_id)
        return list(self.db.execute(stmt).scalars().all())
