"""Question detection and classification engine using multi-signal heuristics."""

import re
import logging
from typing import List, Optional, Tuple, Dict, Any

from app.models.question import QuestionType, ExtractionStatus
from app.processors.interfaces import (
    DetectedQuestion,
    DetectedOption,
    PageExtractionResult,
    QuestionExtractorInterface,
)
from app.processors.option_detector import OptionDetector
from app.utils.text_utils import (
    clean_text,
    normalize_question_number,
    compute_text_completeness_score,
)

logger = logging.getLogger("document_intelligence")

# Regex patterns for detecting question start boundaries
QUESTION_START_PATTERNS = [
    # Question 1: / Question No. 1 / Question 1.
    re.compile(
        r"^(?:Question|Ques|Q)\.?\s*(?:No\.?)?\s*(\d+[a-zA-Z]?)\s*[:\.\)-]\s*(.*)$",
        re.IGNORECASE,
    ),
    # Q1. / Q1: / Q.1: / Q.1
    re.compile(r"^Q\.?\s*(\d+[a-zA-Z]?)\s*[:\.\)-]\s*(.*)$", re.IGNORECASE),
    # 1. / 1) / 1: (must start at beginning of line)
    re.compile(r"^(\d+[a-zA-Z]?)\s*[\.\):\-]\s*(.*)$"),
    # (1) / [1]
    re.compile(r"^[\[\(](\d+[a-zA-Z]?)[\]\)]\s*[:\.\-]?\s*(.*)$"),
]

# Question keywords for classification and validation
QUESTION_KEYWORDS = [
    "what",
    "which",
    "where",
    "when",
    "who",
    "why",
    "how",
    "explain",
    "describe",
    "define",
    "calculate",
    "determine",
    "evaluate",
    "discuss",
    "illustrate",
    "compare",
    "state",
    "find",
    "show",
]


class QuestionDetector(QuestionExtractorInterface):
    """Extracts questions and options across pages using multi-signal heuristics."""

    def __init__(self, option_detector: Optional[OptionDetector] = None):
        self.option_detector = option_detector or OptionDetector()

    def _match_question_start(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Tests if a line matches a question start boundary.
        Returns:
            Tuple of (raw_number, remaining_line_text) or None
        """
        line_str = line.strip()
        for pattern in QUESTION_START_PATTERNS:
            match = pattern.match(line_str)
            if match:
                raw_num = match.group(1)
                text = match.group(2).strip()
                return raw_num, text
        return None

    def classify_question_type(
        self, question_text: str, options: List[DetectedOption]
    ) -> QuestionType:
        """Classifies question type based on options, keywords, and structural patterns."""
        lower_q = question_text.lower()

        # True/False
        if "true or false" in lower_q or (
            len(options) == 2
            and set(opt.text.lower().strip() for opt in options).issubset({"true", "false"})
        ):
            return QuestionType.TRUE_FALSE

        # Fill in the blank
        if "_____" in question_text or "fill in the blank" in lower_q:
            return QuestionType.FILL_IN_THE_BLANK

        # Multiple select vs MCQ
        if options and len(options) >= 2:
            if (
                "select all that apply" in lower_q
                or "which of the following are" in lower_q
                or "choose all" in lower_q
                or "choose two" in lower_q
            ):
                return QuestionType.MULTIPLE_SELECT
            return QuestionType.MCQ

        # Descriptive vs Short Answer
        if any(
            kw in lower_q
            for kw in ["explain in detail", "discuss", "elaborate", "describe in depth", "write an essay"]
        ):
            return QuestionType.DESCRIPTIVE

        if any(lower_q.startswith(kw) for kw in ["define", "name", "state", "what is", "list"]):
            return QuestionType.SHORT_ANSWER

        if any(lower_q.startswith(kw) for kw in QUESTION_KEYWORDS) or "?" in question_text:
            return QuestionType.SHORT_ANSWER

        return QuestionType.UNKNOWN

    def extract_questions_from_page(
        self, page: PageExtractionResult
    ) -> List[DetectedQuestion]:
        """Extracts questions found on a single page."""
        lines = page.text.splitlines()
        raw_blocks: List[Dict[str, Any]] = []

        current_block: Optional[Dict[str, Any]] = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            match = self._match_question_start(line_str)
            if match:
                raw_num, initial_text = match
                # Check if this might just be an option (e.g. 1. Option A)
                # If current block already exists and we see 1. right after A., B., it could be an option
                if current_block:
                    raw_blocks.append(current_block)

                current_block = {
                    "raw_number": raw_num,
                    "lines": [initial_text] if initial_text else [],
                    "page": page.page_number,
                }
            else:
                if current_block:
                    current_block["lines"].append(line_str)
                else:
                    # Text before first question start (could be instructions or header)
                    pass

        if current_block:
            raw_blocks.append(current_block)

        # Parse questions and options from blocks
        detected: List[DetectedQuestion] = []
        for block in raw_blocks:
            full_block_text = "\n".join(block["lines"]).strip()
            q_text, options = self.option_detector.detect_options(full_block_text)

            q_num = normalize_question_number(block["raw_number"])
            q_type = self.classify_question_type(q_text, options)

            # Check completeness and confidence
            completeness = compute_text_completeness_score(q_text)
            ocr_conf = page.confidence
            opt_conf = 0.9 if options else (0.5 if q_type == QuestionType.MCQ else 0.8)
            boundary_conf = 0.9 if block["raw_number"] else 0.5

            confidence = round(
                0.3 * ocr_conf + 0.3 * boundary_conf + 0.2 * opt_conf + 0.2 * completeness,
                2,
            )

            status = ExtractionStatus.SUCCESS
            review_issues = []

            if confidence < 0.65:
                status = ExtractionStatus.REVIEW_REQUIRED
                review_issues.append(
                    {
                        "issue_type": "LOW_OCR_CONFIDENCE"
                        if ocr_conf < 0.7
                        else "QUESTION_BOUNDARY_UNCERTAIN",
                        "severity": "HIGH",
                        "description": f"Question {q_num} has low confidence ({confidence}).",
                    }
                )

            if q_type == QuestionType.UNKNOWN:
                status = ExtractionStatus.REVIEW_REQUIRED
                review_issues.append(
                    {
                        "issue_type": "PARTIAL_QUESTION",
                        "severity": "MEDIUM",
                        "description": f"Could not determine structure or type for Question {q_num}.",
                    }
                )

            detected.append(
                DetectedQuestion(
                    question_number=q_num,
                    question_text=q_text,
                    question_type=q_type,
                    options=options,
                    confidence=confidence,
                    source_start_page=block["page"],
                    source_end_page=block["page"],
                    extraction_status=status,
                    review_issues=review_issues,
                )
            )

        return detected

    def extract_questions(
        self, pages: List[PageExtractionResult]
    ) -> List[DetectedQuestion]:
        """Extracts questions across all pages before multi-page merging."""
        all_questions: List[DetectedQuestion] = []
        for page in pages:
            page_questions = self.extract_questions_from_page(page)
            all_questions.extend(page_questions)
        return all_questions
