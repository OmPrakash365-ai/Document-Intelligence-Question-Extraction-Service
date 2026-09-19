"""Option model."""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.question import Question


class Option(Base):
    __tablename__ = "options"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_key: Mapped[str] = mapped_column(String(20), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationship
    question: Mapped["Question"] = relationship("Question", back_populates="options")


Index("ix_options_question_key", Option.question_id, Option.option_key)
