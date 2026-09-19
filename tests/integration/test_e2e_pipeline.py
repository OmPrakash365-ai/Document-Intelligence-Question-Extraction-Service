"""End-to-End integration tests for extraction pipeline."""

import os
from pathlib import Path
from app.models.document import Document, DocumentStatus
from app.models.question import Question
from app.services.extraction_service import ExtractionService
from app.services.storage_service import LocalStorageService
from app.processors.ocr_processor import MockOCRProvider
from app.processors.page_processor import PageProcessor


def test_e2e_pipeline_clean_digital(db_session, test_user):
    sample_path = Path(__file__).resolve().parent.parent.parent / "sample_documents" / "clean_digital.pdf"
    assert sample_path.exists()

    storage = LocalStorageService()
    # Save file to storage
    with open(sample_path, "rb") as f:
        file_bytes = f.read()
    storage_path = storage.save_file(file_bytes, "clean_digital.pdf", subfolder="original")

    # Create document
    doc = Document(
        owner_id=test_user.id,
        filename="clean_digital.pdf",
        original_filename="clean_digital.pdf",
        content_type="application/pdf",
        file_size=len(file_bytes),
        file_hash="test_clean_hash",
        storage_path=storage_path,
        status=DocumentStatus.QUEUED.value,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    service = ExtractionService(db=db_session, storage=storage)
    processed_doc = service.process_document(doc.id)

    assert processed_doc.status in [DocumentStatus.COMPLETED.value, DocumentStatus.PARTIAL.value]
    assert processed_doc.page_count >= 1
    assert processed_doc.progress == 100

    # Verify questions
    questions = db_session.query(Question).filter(Question.document_id == doc.id).all()
    assert len(questions) >= 3

    # Check Q1 has options
    q1 = next((q for q in questions if q.question_number == "1"), None)
    assert q1 is not None
    assert len(q1.options) == 4
    assert q1.options[0].option_key == "A"


def test_e2e_pipeline_multipage_question(db_session, test_user):
    sample_path = Path(__file__).resolve().parent.parent.parent / "sample_documents" / "multipage_question.pdf"
    assert sample_path.exists()

    storage = LocalStorageService()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()
    storage_path = storage.save_file(file_bytes, "multipage_question.pdf", subfolder="original")

    doc = Document(
        owner_id=test_user.id,
        filename="multipage_question.pdf",
        original_filename="multipage_question.pdf",
        content_type="application/pdf",
        file_size=len(file_bytes),
        file_hash="test_multipage_hash",
        storage_path=storage_path,
        status=DocumentStatus.QUEUED.value,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    service = ExtractionService(db=db_session, storage=storage)
    processed_doc = service.process_document(doc.id)

    assert processed_doc.status in [DocumentStatus.COMPLETED.value, DocumentStatus.PARTIAL.value]
    assert processed_doc.page_count == 2

    # Check that Question 15 was merged across pages [1, 2]
    questions = db_session.query(Question).filter(Question.document_id == doc.id).all()
    q15 = next((q for q in questions if q.question_number == "15"), None)
    assert q15 is not None
    assert q15.source_start_page == 1
    assert q15.source_end_page == 2
    assert len(q15.options) == 4
