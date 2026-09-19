"""Celery asynchronous tasks for document processing and relation matching."""

import logging
import uuid
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.extraction_service import ExtractionService

logger = logging.getLogger("document_intelligence")


@celery_app.task(bind=True, name="app.workers.tasks.process_document_task")
def process_document_task(self, document_id: str):
    """Processes a document asynchronously across all stages."""
    logger.info(f"Starting Celery task for document: {document_id}")
    db = SessionLocal()
    try:
        service = ExtractionService(db)
        doc = service.process_document(uuid.UUID(document_id))
        logger.info(f"Finished processing document: {document_id}, status={doc.status}")
        return {
            "document_id": document_id,
            "status": doc.status,
            "page_count": doc.page_count,
        }
    except Exception as e:
        logger.error(f"Error processing document {document_id} in worker: {str(e)}", exc_info=True)
        raise e
    finally:
        db.close()


@celery_app.task(bind=True, name="app.workers.tasks.match_related_document_answers_task")
def match_related_document_answers_task(self, source_doc_id: str, target_doc_id: str):
    """Re-runs answer matching when a new relation is established."""
    logger.info(
        f"Starting relation answer matching task: source={source_doc_id}, target={target_doc_id}"
    )
    db = SessionLocal()
    try:
        service = ExtractionService(db)
        doc = service.process_document(uuid.UUID(source_doc_id))
        logger.info(
            f"Finished re-matching document {source_doc_id} with answers from {target_doc_id}"
        )
        return {
            "source_doc_id": source_doc_id,
            "target_doc_id": target_doc_id,
            "status": doc.status,
        }
    except Exception as e:
        logger.error(
            f"Error matching answers between {source_doc_id} and {target_doc_id}: {str(e)}",
            exc_info=True,
        )
        raise e
    finally:
        db.close()
