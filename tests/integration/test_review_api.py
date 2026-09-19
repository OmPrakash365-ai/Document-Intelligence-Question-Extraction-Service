"""Integration tests for Review items API endpoints."""

import uuid
from app.models.document import Document, DocumentStatus
from app.models.review_item import ReviewItem, IssueType, Severity


def test_get_document_reviews(client, db_session, test_user, auth_headers):
    # Seed document
    doc = Document(
        owner_id=test_user.id,
        filename="scanned.pdf",
        original_filename="scanned.pdf",
        content_type="application/pdf",
        file_size=1200,
        file_hash="hash_scanned",
        storage_path="/tmp/scanned.pdf",
        status=DocumentStatus.COMPLETED.value,
    )
    db_session.add(doc)
    db_session.commit()

    # Seed review item
    rev = ReviewItem(
        document_id=doc.id,
        issue_type=IssueType.LOW_OCR_CONFIDENCE.value,
        description="OCR confidence below threshold on page 1.",
        severity=Severity.HIGH.value,
        resolved=False,
    )
    db_session.add(rev)
    db_session.commit()

    # Get reviews
    res = client.get(f"/api/v1/documents/{doc.id}/reviews", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["issue_type"] == "LOW_OCR_CONFIDENCE"
    assert item["severity"] == "HIGH"
    assert item["resolved"] is False
