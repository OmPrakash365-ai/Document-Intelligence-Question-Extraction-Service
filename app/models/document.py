"""Document model."""

import enum
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.page import DocumentPage
    from app.models.question import Question
    from app.models.review_item import ReviewItem
    from app.models.document_relation import DocumentRelation


class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class DocumentType(str, enum.Enum):
    QUESTION_PAPER = "QUESTION_PAPER"
    ANSWER_KEY = "ANSWER_KEY"
    UNKNOWN = "UNKNOWN"


class ProcessingStage(str, enum.Enum):
    UPLOADING = "UPLOADING"
    VALIDATING = "VALIDATING"
    EXTRACTING_TEXT = "EXTRACTING_TEXT"
    OCR = "OCR"
    DETECTING_QUESTIONS = "DETECTING_QUESTIONS"
    MATCHING_ANSWERS = "MATCHING_ANSWERS"
    VALIDATING_RESULTS = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), default=DocumentStatus.UPLOADED.value, nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(
        String(50), default=DocumentType.UNKNOWN.value, nullable=False
    )
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_stage: Mapped[str] = mapped_column(
        String(50), default=ProcessingStage.UPLOADING.value, nullable=False
    )
    pages_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    processing_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    pages: Mapped[List["DocumentPage"]] = relationship(
        "DocumentPage", back_populates="document", cascade="all, delete-orphan"
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="document", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["ReviewItem"]] = relationship(
        "ReviewItem", back_populates="document", cascade="all, delete-orphan"
    )
    relations_as_source: Mapped[List["DocumentRelation"]] = relationship(
        "DocumentRelation",
        foreign_keys="DocumentRelation.source_document_id",
        back_populates="source_document",
        cascade="all, delete-orphan",
    )
    relations_as_target: Mapped[List["DocumentRelation"]] = relationship(
        "DocumentRelation",
        foreign_keys="DocumentRelation.target_document_id",
        back_populates="target_document",
        cascade="all, delete-orphan",
    )


# Additional indexes
Index("ix_documents_owner_status", Document.owner_id, Document.status)
