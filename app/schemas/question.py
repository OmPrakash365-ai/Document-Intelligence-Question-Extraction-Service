"""Question and Option Pydantic schemas."""

import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.question import QuestionType, ExtractionStatus
from app.models.answer import MatchingStatus


class OptionItem(BaseModel):
    key: str
    text: str
    confidence: Optional[float] = 1.0

    model_config = ConfigDict(from_attributes=True)


class QuestionAnswer(BaseModel):
    value: str
    confidence: float
    matching_status: MatchingStatus
    source_document_id: Optional[uuid.UUID] = None
    source_page: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionSource(BaseModel):
    document_id: uuid.UUID
    pages: List[int]


class QuestionResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    question_number: str
    question: str
    question_type: QuestionType
    options: List[OptionItem] = Field(default_factory=list)
    answer: Optional[QuestionAnswer] = None
    source: QuestionSource
    confidence: float = Field(..., ge=0.0, le=1.0)
    extraction_status: ExtractionStatus

    model_config = ConfigDict(from_attributes=True)


class QuestionListResponse(BaseModel):
    items: List[QuestionResponse]
    total: int
    page: int
    size: int
    pages: int
