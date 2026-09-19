"""Review item Pydantic schemas."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.review_item import IssueType, Severity


class ReviewItemResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    question_id: Optional[uuid.UUID] = None
    issue_type: IssueType
    description: str
    severity: Severity
    resolved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewItemListResponse(BaseModel):
    items: List[ReviewItemResponse]
    total: int
