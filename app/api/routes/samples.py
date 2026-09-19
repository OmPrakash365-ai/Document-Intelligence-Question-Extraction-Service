"""Sample documents API routes for 1-click testing in the UI."""

from pathlib import Path
from fastapi import APIRouter, Depends, status, UploadFile
from sqlalchemy.orm import Session
import io

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import DocumentStatus
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import DocumentService
from app.core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/documents/sample", tags=["Sample Documents"])

SAMPLE_MAP = {
    "clean_digital": ("clean_digital.pdf", "application/pdf"),
    "multipage_question": ("multipage_question.pdf", "application/pdf"),
    "exam_with_inline_answers": ("exam_with_inline_answers.pdf", "application/pdf"),
    "question_paper_png": ("question_paper.png", "image/png"),
    "question_paper_jpg": ("question_paper.jpg", "image/jpeg"),
    "scanned_exam": ("scanned_exam.pdf", "application/pdf"),
    "separate_answer_key": ("separate_answer_key.pdf", "application/pdf"),
}


@router.post(
    "/{sample_name}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="1-Click Sample Document Upload",
    description="Loads and queues a pre-generated sample document for immediate testing.",
)
def upload_sample_document(
    sample_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    if sample_name not in SAMPLE_MAP:
        raise ResourceNotFoundError(
            f"Sample '{sample_name}' not found. Available: {', '.join(SAMPLE_MAP.keys())}"
        )

    filename, content_type = SAMPLE_MAP[sample_name]
    sample_path = Path(__file__).resolve().parent.parent.parent.parent / "sample_documents" / filename

    if not sample_path.exists():
        raise ResourceNotFoundError(f"Sample file {filename} not found on disk.")

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    upload_file = UploadFile(
        filename=filename,
        file=io.BytesIO(file_bytes),
        headers={"content-type": content_type},
    )

    service = DocumentService(db)
    doc = service.upload_document(upload_file, current_user)

    return DocumentUploadResponse(
        document_id=doc.id,
        status=DocumentStatus(doc.status),
        message=f"Sample document '{filename}' uploaded and queued for processing.",
    )
