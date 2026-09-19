"""Document repository for database operations."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import Session, selectinload

from app.models.document import Document, DocumentStatus
from app.models.page import DocumentPage


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = (
            select(Document)
            .options(
                selectinload(Document.pages),
                selectinload(Document.questions),
                selectinload(Document.reviews),
            )
            .where(Document.id == document_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_hash_and_owner(
        self, file_hash: str, owner_id: uuid.UUID
    ) -> Optional[Document]:
        stmt = select(Document).where(
            Document.file_hash == file_hash, Document.owner_id == owner_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_owner(
        self,
        owner_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[Document], int]:
        stmt = select(Document).where(Document.owner_id == owner_id)
        if status:
            stmt = stmt.where(Document.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(Document.created_at.desc()).offset((page - 1) * size).limit(size)
        items = self.db.execute(stmt).scalars().all()
        return list(items), total

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update_status(
        self,
        document_id: uuid.UUID,
        status: str,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        pages_processed: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Document]:
        doc = self.get_by_id(document_id)
        if not doc:
            return None

        doc.status = status
        if stage:
            doc.current_stage = stage
        if progress is not None:
            doc.progress = progress
        if pages_processed is not None:
            doc.pages_processed = pages_processed
        if error_message is not None:
            doc.error_message = error_message

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, document_id: uuid.UUID) -> bool:
        doc = self.get_by_id(document_id)
        if not doc:
            return False
        self.db.delete(doc)
        self.db.commit()
        return True

    def save_page(self, page: DocumentPage) -> DocumentPage:
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def get_page(
        self, document_id: uuid.UUID, page_number: int
    ) -> Optional[DocumentPage]:
        stmt = select(DocumentPage).where(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == page_number,
        )
        return self.db.execute(stmt).scalar_one_or_none()
