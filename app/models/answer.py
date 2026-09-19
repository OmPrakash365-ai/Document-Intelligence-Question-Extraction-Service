"""Answer model."""

import enum
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.document import Document


class MatchingStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    UNCERTAIN = "UNCERTAIN"
    UNMATCHED = "UNMATCHED"


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("questions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    answer_value: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(
        String(50), default="OPTION_KEY", nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    matching_status: Mapped[str] = mapped_column(
        String(50), default=MatchingStatus.UNMATCHED.value, nullable=False, index=True
    )

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="answer")
    source_document: Mapped[Optional["Document"]] = relationship("Document")
