"""Document relation repository."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_relation import DocumentRelation


class DocumentRelationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, relation_id: uuid.UUID) -> Optional[DocumentRelation]:
        stmt = select(DocumentRelation).where(DocumentRelation.id == relation_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_source_and_target(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> Optional[DocumentRelation]:
        stmt = select(DocumentRelation).where(
            DocumentRelation.source_document_id == source_id,
            DocumentRelation.target_document_id == target_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_document(self, document_id: uuid.UUID) -> List[DocumentRelation]:
        stmt = select(DocumentRelation).where(
            (DocumentRelation.source_document_id == document_id)
            | (DocumentRelation.target_document_id == document_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(self, relation: DocumentRelation) -> DocumentRelation:
        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)
        return relation

    def delete(self, relation_id: uuid.UUID) -> bool:
        relation = self.get_by_id(relation_id)
        if not relation:
            return False
        self.db.delete(relation)
        self.db.commit()
        return True
