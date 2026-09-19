"""Document service managing uploads, status, queries, and deletion."""

import os
import uuid
from typing import List, Optional, Tuple, BinaryIO
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    DocumentNotFoundError,
    UnauthorizedAccessError,
    MalformedFileError,
)
from app.models.document import Document, DocumentStatus, DocumentType, ProcessingStage
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import get_storage_service, StorageService
from app.utils.file_validation import (
    validate_file_extension,
    validate_file_size,
    validate_file_content,
    generate_secure_storage_filename,
)
from app.utils.hashing import calculate_sha256

settings = get_settings()


class DocumentService:
    def __init__(self, db: Session, storage: Optional[StorageService] = None):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = storage or get_storage_service()

    def upload_document(
        self, file: UploadFile, current_user: User
    ) -> Document:
        """Validates, stores, and registers an uploaded document."""
        # 1. Read file header to validate magic bytes and compute size
        file_bytes = file.file.read()
        file_size = len(file_bytes)

        # Validate extension & size
        ext = validate_file_extension(file.filename)
        validate_file_size(file_size)

        # Validate magic bytes
        validate_file_content(file_bytes[:16], ext)

        # Compute SHA-256 hash
        file_hash = calculate_sha256(file_bytes)

        # Generate secure random storage filename
        secure_filename, _ = generate_secure_storage_filename(file.filename)

        # Save to storage
        storage_path = self.storage.save_file(
            file_bytes, secure_filename, subfolder="original"
        )

        # Create database record
        doc = Document(
            owner_id=current_user.id,
            filename=secure_filename,
            original_filename=file.filename,
            content_type=file.content_type or f"application/{ext}",
            file_size=file_size,
            file_hash=file_hash,
            storage_path=storage_path,
            status=DocumentStatus.QUEUED.value,
            current_stage=ProcessingStage.UPLOADING.value,
            progress=0,
        )
        created_doc = self.repo.create(doc)

        # Trigger Celery background task
        # Import task lazily to avoid circular dependencies
        from app.workers.tasks import process_document_task

        try:
            process_document_task.delay(str(created_doc.id))
        except Exception:
            # If celery broker is offline in local dev, allow task to be run or flagged
            pass

        return created_doc

    def get_document(
        self, document_id: uuid.UUID, current_user: User
    ) -> Document:
        doc = self.repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        if doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("You do not have permission to access this document.")
        return doc

    def list_documents(
        self,
        current_user: User,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[Document], int]:
        return self.repo.list_by_owner(
            owner_id=current_user.id, page=page, size=size, status=status
        )

    def delete_document(
        self, document_id: uuid.UUID, current_user: User
    ) -> bool:
        doc = self.get_document(document_id, current_user)
        # Delete from storage
        self.storage.delete_file(doc.filename, subfolder="original")
        # Delete from DB
        return self.repo.delete(document_id)
