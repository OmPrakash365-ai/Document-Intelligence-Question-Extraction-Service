"""Review Item model."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.question import Question


class IssueType(str, enum.Enum):
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"
    MISSING_QUESTION_NUMBER = "MISSING_QUESTION_NUMBER"
    PARTIAL_QUESTION = "PARTIAL_QUESTION"
    QUESTION_BOUNDARY_UNCERTAIN = "QUESTION_BOUNDARY_UNCERTAIN"
    OPTIONS_UNCERTAIN = "OPTIONS_UNCERTAIN"
    ANSWER_UNMATCHED = "ANSWER_UNMATCHED"
    ANSWER_LOW_CONFIDENCE = "ANSWER_LOW_CONFIDENCE"
    OCR_ERROR = "OCR_ERROR"
    MULTI_PAGE_MERGE_UNCERTAIN = "MULTI_PAGE_MERGE_UNCERTAIN"


class Severity(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("questions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default=Severity.MEDIUM.value, nullable=False, index=True
    )
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="reviews")
    question: Mapped[Optional["Question"]] = relationship(
        "Question", back_populates="review_items"
    )


Index("ix_review_items_doc_severity", ReviewItem.document_id, ReviewItem.severity)
