"""Review item repository."""

import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.review_item import ReviewItem


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: uuid.UUID) -> Optional[ReviewItem]:
        stmt = select(ReviewItem).where(ReviewItem.id == review_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_document(
        self, document_id: uuid.UUID, resolved: Optional[bool] = None
    ) -> List[ReviewItem]:
        stmt = select(ReviewItem).where(ReviewItem.document_id == document_id)
        if resolved is not None:
            stmt = stmt.where(ReviewItem.resolved == resolved)
        stmt = stmt.order_by(ReviewItem.created_at.asc())
        return list(self.db.execute(stmt).scalars().all())

    def save_review_items(
        self, review_items: List[ReviewItem]
    ) -> List[ReviewItem]:
        for item in review_items:
            self.db.add(item)
        self.db.commit()
        for item in review_items:
            self.db.refresh(item)
        return review_items

    def delete_by_document(self, document_id: uuid.UUID) -> int:
        stmt = select(ReviewItem).where(ReviewItem.document_id == document_id)
        items = self.db.execute(stmt).scalars().all()
        count = len(items)
        for item in items:
            self.db.delete(item)
        self.db.commit()
        return count
