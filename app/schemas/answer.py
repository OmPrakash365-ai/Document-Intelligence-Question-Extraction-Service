"""Answer Pydantic schemas."""

import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.answer import MatchingStatus


class AnswerResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    value: str
    answer_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    matching_status: MatchingStatus
    source_document_id: Optional[uuid.UUID] = None
    source_page: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
