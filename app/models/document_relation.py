"""Document Relation model."""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.document import Document


class RelationType(str, enum.Enum):
    QUESTION_PAPER = "QUESTION_PAPER"
    ANSWER_KEY = "ANSWER_KEY"
    RELATED_DOCUMENT = "RELATED_DOCUMENT"


class DocumentRelation(Base):
    __tablename__ = "document_relations"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[str] = mapped_column(
        String(50), default=RelationType.RELATED_DOCUMENT.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    source_document: Mapped["Document"] = relationship(
        "Document",
        foreign_keys=[source_document_id],
        back_populates="relations_as_source",
    )
    target_document: Mapped["Document"] = relationship(
        "Document",
        foreign_keys=[target_document_id],
        back_populates="relations_as_target",
    )


Index(
    "ix_document_relations_source_target",
    DocumentRelation.source_document_id,
    DocumentRelation.target_document_id,
    unique=True,
)
