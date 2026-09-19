"""Document Pydantic schemas."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.document import DocumentStatus, DocumentType, ProcessingStage
from app.models.document_relation import RelationType


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: DocumentStatus
    message: str = "Document uploaded and queued for processing"


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: DocumentStatus
    progress: int = Field(..., ge=0, le=100, description="Processing progress from 0 to 100")
    current_stage: ProcessingStage
    pages_processed: int
    total_pages: int


class DocumentResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    file_hash: str
    status: DocumentStatus
    document_type: DocumentType
    page_count: int
    progress: int
    current_stage: ProcessingStage
    pages_processed: int
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentPageResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    extracted_text: Optional[str] = None
    ocr_used: bool
    image_path: Optional[str] = None
    processing_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRelationCreate(BaseModel):
    target_document_id: uuid.UUID
    relation_type: RelationType = RelationType.ANSWER_KEY


class DocumentRelationResponse(BaseModel):
    id: uuid.UUID
    source_document_id: uuid.UUID
    target_document_id: uuid.UUID
    relation_type: RelationType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
