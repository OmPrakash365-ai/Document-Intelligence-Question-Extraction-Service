"""Review items API routes."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import ReviewItemListResponse, ReviewItemResponse
from app.repositories.review_repository import ReviewRepository
from app.repositories.document_repository import DocumentRepository
from app.core.exceptions import DocumentNotFoundError, UnauthorizedAccessError

router = APIRouter(tags=["Reviews"])


@router.get(
    "/documents/{document_id}/reviews",
    response_model=ReviewItemListResponse,
    summary="Get document review items",
    description="Returns all review items and extraction warnings for uncertain questions, OCR quality issues, or unmatched answers.",
)
def get_document_reviews(
    document_id: uuid.UUID,
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewItemListResponse:
    doc_repo = DocumentRepository(db)
    doc = doc_repo.get_by_id(document_id)
    if not doc:
        raise DocumentNotFoundError(str(document_id))
    if doc.owner_id != current_user.id:
        raise UnauthorizedAccessError("Unauthorized access to document reviews.")

    review_repo = ReviewRepository(db)
    items = review_repo.list_by_document(document_id, resolved=resolved)
    return ReviewItemListResponse(
        items=[ReviewItemResponse.model_validate(item) for item in items],
        total=len(items),
    )
