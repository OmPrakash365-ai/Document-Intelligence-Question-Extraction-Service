"""Document relation service for linking question papers and answer keys."""

import uuid
from typing import List
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DocumentNotFoundError,
    UnauthorizedAccessError,
    ConflictError,
    ResourceNotFoundError,
)
from app.models.user import User
from app.models.document_relation import DocumentRelation, RelationType
from app.models.document import Document
from app.repositories.relation_repository import DocumentRelationRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentRelationResponse


class RelationService:
    def __init__(self, db: Session):
        self.db = db
        self.relation_repo = DocumentRelationRepository(db)
        self.doc_repo = DocumentRepository(db)

    def create_relation(
        self,
        source_document_id: uuid.UUID,
        target_document_id: uuid.UUID,
        relation_type: RelationType,
        current_user: User,
    ) -> DocumentRelationResponse:
        # Check source document
        source_doc = self.doc_repo.get_by_id(source_document_id)
        if not source_doc:
            raise DocumentNotFoundError(str(source_document_id))
        if source_doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("Unauthorized access to source document.")

        # Check target document
        target_doc = self.doc_repo.get_by_id(target_document_id)
        if not target_doc:
            raise DocumentNotFoundError(str(target_document_id))
        if target_doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("Unauthorized access to target document.")

        # Check if already related
        existing = self.relation_repo.get_by_source_and_target(
            source_document_id, target_document_id
        )
        if existing:
            raise ConflictError("These documents are already related.")

        relation = DocumentRelation(
            source_document_id=source_document_id,
            target_document_id=target_document_id,
            relation_type=relation_type.value,
        )
        created = self.relation_repo.create(relation)

        # Trigger re-extraction / answer matching task asynchronously
        try:
            from app.workers.tasks import match_related_document_answers_task

            match_related_document_answers_task.delay(
                str(source_document_id), str(target_document_id)
            )
        except Exception:
            pass

        return DocumentRelationResponse.model_validate(created)

    def list_relations(
        self, document_id: uuid.UUID, current_user: User
    ) -> List[DocumentRelationResponse]:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        if doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("Unauthorized access to document relations.")

        relations = self.relation_repo.list_by_document(document_id)
        return [DocumentRelationResponse.model_validate(r) for r in relations]

    def delete_relation(
        self,
        document_id: uuid.UUID,
        relation_id: uuid.UUID,
        current_user: User,
    ) -> bool:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc or doc.owner_id != current_user.id:
            raise UnauthorizedAccessError("Unauthorized access to document.")

        rel = self.relation_repo.get_by_id(relation_id)
        if not rel or (rel.source_document_id != document_id and rel.target_document_id != document_id):
            raise ResourceNotFoundError(f"Relation {relation_id} not found.")

        return self.relation_repo.delete(relation_id)
