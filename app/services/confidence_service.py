"""Confidence scoring and review item generation service."""

import logging
from typing import List, Optional, Tuple
from app.core.config import get_settings
from app.models.review_item import ReviewItem, IssueType, Severity
from app.models.answer import MatchingStatus
from app.processors.interfaces import DetectedQuestion, DetectedAnswer

logger = logging.getLogger("document_intelligence")
settings = get_settings()


class ConfidenceService:
    """Calculates deterministic confidence scores and generates review items."""

    def calculate_question_confidence(
        self,
        ocr_confidence: float,
        boundary_confidence: float,
        option_confidence: float,
        text_completeness: float,
        answer: Optional[DetectedAnswer] = None,
    ) -> Tuple[float, List[dict]]:
        """
        Calculates confidence score between 0.0 and 1.0 using deterministic formula:
        overall = 0.25 * OCR + 0.25 * boundary + 0.20 * option + 0.15 * completeness + 0.15 * answer_matching
        """
        answer_conf = 0.0
        if answer:
            if answer.matching_status == MatchingStatus.MATCHED:
                answer_conf = answer.confidence
            elif answer.matching_status == MatchingStatus.UNCERTAIN:
                answer_conf = answer.confidence * 0.5
            else:
                answer_conf = 0.0
        else:
            # If answer is unavailable, do not artificially inflate score
            answer_conf = 0.0

        overall = (
            0.25 * ocr_confidence
            + 0.25 * boundary_confidence
            + 0.20 * option_confidence
            + 0.15 * text_completeness
            + 0.15 * answer_conf
        )

        overall = round(min(1.0, max(0.0, overall)), 2)

        review_issues = []

        if ocr_confidence < 0.70:
            review_issues.append(
                {
                    "issue_type": IssueType.LOW_OCR_CONFIDENCE.value,
                    "severity": Severity.HIGH.value if ocr_confidence < 0.5 else Severity.MEDIUM.value,
                    "description": f"Page OCR confidence was low ({ocr_confidence:.2f}).",
                }
            )

        if text_completeness < 0.50:
            review_issues.append(
                {
                    "issue_type": IssueType.PARTIAL_QUESTION.value,
                    "severity": Severity.MEDIUM.value,
                    "description": "Question text appears incomplete or truncated.",
                }
            )

        if option_confidence < 0.70:
            review_issues.append(
                {
                    "issue_type": IssueType.OPTIONS_UNCERTAIN.value,
                    "severity": Severity.MEDIUM.value,
                    "description": "Question options could not be cleanly identified.",
                }
            )

        if answer:
            if answer.matching_status == MatchingStatus.UNCERTAIN:
                review_issues.append(
                    {
                        "issue_type": IssueType.ANSWER_LOW_CONFIDENCE.value,
                        "severity": Severity.MEDIUM.value,
                        "description": f"Answer matched with uncertainty ({answer.confidence:.2f}).",
                    }
                )
        else:
            review_issues.append(
                {
                    "issue_type": IssueType.ANSWER_UNMATCHED.value,
                    "severity": Severity.LOW.value,
                    "description": "No corresponding answer key was found for this question.",
                }
            )

        return overall, review_issues
