"""Extraction service orchestrating the multi-stage document intelligence pipeline."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document, DocumentStatus, DocumentType, ProcessingStage
from app.models.page import DocumentPage
from app.models.question import Question, QuestionType, ExtractionStatus
from app.models.option import Option
from app.models.answer import Answer, MatchingStatus
from app.models.review_item import ReviewItem, IssueType, Severity
from app.models.document_relation import DocumentRelation, RelationType
from app.repositories.document_repository import DocumentRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.answer_repository import AnswerRepository
from app.repositories.review_repository import ReviewRepository
from app.processors.page_processor import PageProcessor
from app.processors.question_detector import QuestionDetector
from app.processors.question_merger import QuestionMerger
from app.processors.answer_key_detector import AnswerKeyDetector
from app.services.confidence_service import ConfidenceService
from app.services.storage_service import get_storage_service, StorageService

logger = logging.getLogger("document_intelligence")
settings = get_settings()


class ExtractionService:
    def __init__(
        self,
        db: Session,
        storage: Optional[StorageService] = None,
        page_processor: Optional[PageProcessor] = None,
        question_detector: Optional[QuestionDetector] = None,
        question_merger: Optional[QuestionMerger] = None,
        answer_key_detector: Optional[AnswerKeyDetector] = None,
        confidence_service: Optional[ConfidenceService] = None,
    ):
        self.db = db
        self.storage = storage or get_storage_service()
        self.doc_repo = DocumentRepository(db)
        self.question_repo = QuestionRepository(db)
        self.answer_repo = AnswerRepository(db)
        self.review_repo = ReviewRepository(db)

        self.page_processor = page_processor or PageProcessor()
        self.question_detector = question_detector or QuestionDetector()
        self.question_merger = question_merger or QuestionMerger()
        self.answer_key_detector = answer_key_detector or AnswerKeyDetector()
        self.confidence_service = confidence_service or ConfidenceService()

    def process_document(self, document_id: uuid.UUID) -> Document:
        """Executes the full asynchronous document extraction pipeline."""
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        try:
            # 1. Start processing
            doc.status = DocumentStatus.PROCESSING.value
            doc.current_stage = ProcessingStage.VALIDATING.value
            doc.processing_started_at = datetime.now(timezone.utc)
            doc.progress = 10
            self.db.commit()

            file_path = self.storage.get_file_path(doc.filename, subfolder="original")
            pages_output_dir = self.storage.get_file_path("", subfolder="pages")

            # 2. Extract pages & OCR
            doc.current_stage = ProcessingStage.EXTRACTING_TEXT.value
            doc.progress = 25
            self.db.commit()

            page_results = self.page_processor.extract_pages(
                file_path, output_image_dir=pages_output_dir
            )

            doc.page_count = len(page_results)
            doc.pages_processed = len(page_results)
            doc.current_stage = ProcessingStage.OCR.value
            doc.progress = 40
            self.db.commit()

            # Save document pages to DB
            for p in page_results:
                page_model = DocumentPage(
                    document_id=doc.id,
                    page_number=p.page_number,
                    extracted_text=p.text,
                    ocr_used=p.ocr_used,
                    image_path=p.image_path,
                    processing_status="COMPLETED",
                )
                self.doc_repo.save_page(page_model)

            # 3. Detect Questions
            doc.current_stage = ProcessingStage.DETECTING_QUESTIONS.value
            doc.progress = 55
            self.db.commit()

            raw_questions = self.question_detector.extract_questions(page_results)

            # 4. Merge multi-page questions
            merged_questions = self.question_merger.merge_multipage_questions(
                raw_questions, page_results
            )

            # 5. Detect and match answers
            doc.current_stage = ProcessingStage.MATCHING_ANSWERS.value
            doc.progress = 75
            self.db.commit()

            # 5a. Detect inline answers in current document
            inline_answers = self.answer_key_detector.extract_answers(page_results)
            answers_map: Dict[str, Any] = {a.question_number: a for a in inline_answers}

            # 5b. Check related answer key documents
            relations = (
                self.db.query(DocumentRelation)
                .filter(
                    DocumentRelation.source_document_id == doc.id,
                    DocumentRelation.relation_type == RelationType.ANSWER_KEY.value,
                )
                .all()
            )
            for rel in relations:
                # Fetch pages from related answer key document
                target_pages = (
                    self.db.query(DocumentPage)
                    .filter(DocumentPage.document_id == rel.target_document_id)
                    .all()
                )
                if target_pages:
                    from app.processors.interfaces import PageExtractionResult

                    target_page_results = [
                        PageExtractionResult(
                            page_number=tp.page_number,
                            text=tp.extracted_text or "",
                            ocr_used=tp.ocr_used,
                        )
                        for tp in target_pages
                    ]
                    related_answers = self.answer_key_detector.extract_answers(
                        target_page_results
                    )
                    for ra in related_answers:
                        ra.source_document_id = str(rel.target_document_id)
                        answers_map[ra.question_number] = ra

            # If document has mostly answers and no questions, classify as ANSWER_KEY
            if len(inline_answers) > 0 and len(merged_questions) == 0:
                doc.document_type = DocumentType.ANSWER_KEY.value
            elif len(merged_questions) > 0:
                doc.document_type = DocumentType.QUESTION_PAPER.value

            # 6. Validate results, calculate confidence, create review items
            doc.current_stage = ProcessingStage.VALIDATING_RESULTS.value
            doc.progress = 90
            self.db.commit()

            # Clear any previous questions/reviews for idempotency
            self.question_repo.delete_by_document(doc.id)
            self.review_repo.delete_by_document(doc.id)

            created_questions: List[Question] = []
            created_review_items: List[ReviewItem] = []

            for q_data in merged_questions:
                matched_ans = answers_map.get(q_data.question_number)

                # Calculate confidence
                opt_conf = 0.95 if q_data.options else 0.8
                completeness = 0.9 if q_data.question_text.endswith(("?", ".", ":")) else 0.6
                ocr_conf = 0.95  # default if digital

                overall_conf, issues = self.confidence_service.calculate_question_confidence(
                    ocr_confidence=ocr_conf,
                    boundary_confidence=0.9,
                    option_confidence=opt_conf,
                    text_completeness=completeness,
                    answer=matched_ans,
                )

                # Determine extraction status
                q_status = ExtractionStatus.SUCCESS.value
                if overall_conf < settings.MEDIUM_CONFIDENCE_THRESHOLD:
                    q_status = ExtractionStatus.REVIEW_REQUIRED.value

                question_model = Question(
                    document_id=doc.id,
                    question_number=q_data.question_number,
                    question_text=q_data.question_text,
                    question_type=q_data.question_type.value,
                    confidence=overall_conf,
                    extraction_status=q_status,
                    source_start_page=q_data.source_start_page,
                    source_end_page=q_data.source_end_page,
                )

                # Add options
                for opt in q_data.options:
                    option_model = Option(
                        option_key=opt.key,
                        option_text=opt.text,
                        confidence=opt.confidence,
                    )
                    question_model.options.append(option_model)

                # Add answer if matched
                if matched_ans:
                    answer_model = Answer(
                        answer_value=matched_ans.answer_value,
                        answer_type=matched_ans.answer_type,
                        confidence=matched_ans.confidence,
                        source_document_id=uuid.UUID(matched_ans.source_document_id)
                        if matched_ans.source_document_id
                        else doc.id,
                        source_page=matched_ans.source_page,
                        matching_status=matched_ans.matching_status.value,
                    )
                    question_model.answer = answer_model

                self.db.add(question_model)
                self.db.flush()  # to populate question_model.id

                # Collect review items
                all_issues = q_data.review_issues + issues
                for issue in all_issues:
                    rev_item = ReviewItem(
                        document_id=doc.id,
                        question_id=question_model.id,
                        issue_type=issue["issue_type"],
                        description=issue["description"],
                        severity=issue["severity"],
                        resolved=False,
                    )
                    created_review_items.append(rev_item)

            if created_review_items:
                self.review_repo.save_review_items(created_review_items)

            # 7. Complete processing
            doc.status = (
                DocumentStatus.PARTIAL.value
                if any(
                    q.extraction_status == ExtractionStatus.REVIEW_REQUIRED.value
                    for q in created_questions
                )
                else DocumentStatus.COMPLETED.value
            )
            doc.current_stage = ProcessingStage.COMPLETED.value
            doc.progress = 100
            doc.processing_completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(doc)
            return doc

        except Exception as e:
            logger.error(
                f"Document processing failed for {document_id}: {str(e)}",
                exc_info=True,
            )
            doc.status = DocumentStatus.FAILED.value
            doc.current_stage = ProcessingStage.FAILED.value
            doc.error_message = str(e)
            doc.processing_completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return doc
