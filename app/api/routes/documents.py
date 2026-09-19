"""Document management API routes."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import DocumentStatus
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentListResponse,
    DocumentPageResponse,
    DocumentRelationCreate,
    DocumentRelationResponse,
)
from app.services.document_service import DocumentService
from app.services.relation_service import RelationService
from app.repositories.document_repository import DocumentRepository
from app.core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a document",
    description="Accepts a PDF or image file (JPG, JPEG, PNG), validates it, stores it, and enqueues it for asynchronous processing.",
)
def upload_document(
    file: UploadFile = File(..., description="Document file to upload (PDF, JPG, PNG)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    service = DocumentService(db)
    doc = service.upload_document(file, current_user)
    return DocumentUploadResponse(
        document_id=doc.id,
        status=DocumentStatus(doc.status),
        message="Document uploaded and queued for processing",
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List uploaded documents",
    description="Returns a paginated list of documents owned by the authenticated user.",
)
def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    service = DocumentService(db)
    items, total = service.list_documents(
        current_user=current_user, page=page, size=size, status=status
    )
    pages = (total + size - 1) // size if total > 0 else 0
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Returns detailed metadata and processing metrics for a document.",
)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    service = DocumentService(db)
    doc = service.get_document(document_id, current_user)
    return DocumentResponse.model_validate(doc)


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Check document processing status",
    description="Returns the current processing status, stage, progress percentage, and page counts.",
)
def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentStatusResponse:
    service = DocumentService(db)
    doc = service.get_document(document_id, current_user)
    return DocumentStatusResponse(
        document_id=doc.id,
        status=DocumentStatus(doc.status),
        progress=doc.progress,
        current_stage=doc.current_stage,
        pages_processed=doc.pages_processed,
        total_pages=doc.page_count,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Permanently deletes a document, its extracted pages, questions, answers, and stored files.",
)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)
    service.delete_document(document_id, current_user)
    return None


@router.get(
    "/{document_id}/pages/{page_number}",
    response_model=DocumentPageResponse,
    summary="Get document page details",
    description="Returns extracted text, OCR status, and image path for a specific document page.",
)
def get_document_page(
    document_id: uuid.UUID,
    page_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentPageResponse:
    service = DocumentService(db)
    doc = service.get_document(document_id, current_user)
    repo = DocumentRepository(db)
    page = repo.get_page(document_id, page_number)
    if not page:
        raise ResourceNotFoundError(
            f"Page {page_number} not found for document {document_id}"
        )
    return DocumentPageResponse.model_validate(page)


@router.post(
    "/{document_id}/relations",
    response_model=DocumentRelationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create document relationship",
    description="Links two documents together (e.g. a Question Paper and an Answer Key).",
)
def create_relation(
    document_id: uuid.UUID,
    relation_in: DocumentRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRelationResponse:
    service = RelationService(db)
    return service.create_relation(
        source_document_id=document_id,
        target_document_id=relation_in.target_document_id,
        relation_type=relation_in.relation_type,
        current_user=current_user,
    )


@router.get(
    "/{document_id}/relations",
    response_model=list[DocumentRelationResponse],
    summary="List document relations",
    description="Returns all relations associated with a document.",
)
def list_relations(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRelationResponse]:
    service = RelationService(db)
    return service.list_relations(document_id, current_user)


@router.delete(
    "/{document_id}/relations/{relation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document relation",
    description="Removes a relationship between two documents.",
)
def delete_relation(
    document_id: uuid.UUID,
    relation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RelationService(db)
    service.delete_relation(document_id, relation_id, current_user)
    return None
