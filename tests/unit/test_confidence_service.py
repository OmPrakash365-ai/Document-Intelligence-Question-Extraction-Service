"""Unit tests for confidence scoring service."""

from app.services.confidence_service import ConfidenceService
from app.processors.interfaces import DetectedAnswer
from app.models.answer import MatchingStatus
from app.models.review_item import IssueType


def test_confidence_calculation_high():
    service = ConfidenceService()
    ans = DetectedAnswer(
        question_number="1",
        answer_value="A",
        confidence=0.95,
        matching_status=MatchingStatus.MATCHED,
    )
    score, issues = service.calculate_question_confidence(
        ocr_confidence=0.95,
        boundary_confidence=0.95,
        option_confidence=0.95,
        text_completeness=0.95,
        answer=ans,
    )
    # 0.25*0.95 + 0.25*0.95 + 0.20*0.95 + 0.15*0.95 + 0.15*0.95 = 0.95
    assert score >= 0.85
    assert len(issues) == 0


def test_confidence_calculation_low_ocr():
    service = ConfidenceService()
    score, issues = service.calculate_question_confidence(
        ocr_confidence=0.40,
        boundary_confidence=0.80,
        option_confidence=0.80,
        text_completeness=0.80,
        answer=None,
    )
    # OCR is < 0.70, should generate LOW_OCR_CONFIDENCE
    issue_types = [i["issue_type"] for i in issues]
    assert IssueType.LOW_OCR_CONFIDENCE.value in issue_types
    assert IssueType.ANSWER_UNMATCHED.value in issue_types


def test_confidence_no_answer_does_not_inflate():
    service = ConfidenceService()
    score_no_ans, _ = service.calculate_question_confidence(
        ocr_confidence=0.90,
        boundary_confidence=0.90,
        option_confidence=0.90,
        text_completeness=0.90,
        answer=None,
    )
    # Without answer, score is 0.85 * 0.90 = 0.765 (rounded to 0.76 or 0.77)
    assert score_no_ans < 0.85
