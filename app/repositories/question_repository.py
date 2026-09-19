"""Question repository for database queries and persistence."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.models.question import Question
from app.models.option import Option


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: uuid.UUID) -> Optional[Question]:
        stmt = (
            select(Question)
            .options(
                selectinload(Question.options),
                selectinload(Question.answer),
                selectinload(Question.review_items),
            )
            .where(Question.id == question_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_document(
        self,
        document_id: uuid.UUID,
        page: int = 1,
        size: int = 50,
    ) -> Tuple[List[Question], int]:
        stmt = (
            select(Question)
            .options(
                selectinload(Question.options),
                selectinload(Question.answer),
            )
            .where(Question.document_id == document_id)
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Try to order by integer question_number if numeric, otherwise string
        stmt = stmt.order_by(Question.source_start_page.asc(), Question.id.asc()).offset(
            (page - 1) * size
        ).limit(size)
        items = self.db.execute(stmt).scalars().all()
        return list(items), total

    def save_questions(self, questions: List[Question]) -> List[Question]:
        for q in questions:
            self.db.add(q)
        self.db.commit()
        for q in questions:
            self.db.refresh(q)
        return questions

    def delete_by_document(self, document_id: uuid.UUID) -> int:
        stmt = select(Question).where(Question.document_id == document_id)
        questions = self.db.execute(stmt).scalars().all()
        count = len(questions)
        for q in questions:
            self.db.delete(q)
        self.db.commit()
        return count
