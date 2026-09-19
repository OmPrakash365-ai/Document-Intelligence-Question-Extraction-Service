"""Question model."""

import enum
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.option import Option
    from app.models.answer import Answer
    from app.models.review_item import ReviewItem


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    MULTIPLE_SELECT = "MULTIPLE_SELECT"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_IN_THE_BLANK = "FILL_IN_THE_BLANK"
    SHORT_ANSWER = "SHORT_ANSWER"
    DESCRIPTIVE = "DESCRIPTIVE"
    UNKNOWN = "UNKNOWN"


class ExtractionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_number: Mapped[str] = mapped_column(String(50), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), default=QuestionType.UNKNOWN.value, nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    extraction_status: Mapped[str] = mapped_column(
        String(50), default=ExtractionStatus.SUCCESS.value, nullable=False
    )
    source_start_page: Mapped[int] = mapped_column(Integer, nullable=False)
    source_end_page: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="questions")
    options: Mapped[List["Option"]] = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Option.option_key",
    )
    answer: Mapped[Optional["Answer"]] = relationship(
        "Answer",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )
    review_items: Mapped[List["ReviewItem"]] = relationship(
        "ReviewItem",
        back_populates="question",
        cascade="all, delete-orphan",
    )


Index("ix_questions_doc_number", Question.document_id, Question.question_number)
