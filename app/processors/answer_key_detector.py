"""Answer key detection and parser engine."""

import re
import logging
from typing import List, Optional, Dict
from app.models.answer import MatchingStatus
from app.processors.interfaces import (
    DetectedAnswer,
    PageExtractionResult,
    AnswerKeyExtractorInterface,
)
from app.utils.text_utils import normalize_question_number, normalize_option_key

logger = logging.getLogger("document_intelligence")

# Answer Key section markers
ANSWER_SECTION_PATTERNS = [
    re.compile(r"^(?:Answer\s*Key|Answers|Solution\s*Key|Key\s*Answers)[\s:]*$", re.IGNORECASE | re.MULTILINE),
]

# Patterns for individual answer entries:
# 1. "1. A" or "1. (A)"
# 2. "1-A" or "1 - A" or "1- (B)"
# 3. "Q1: A" or "Q.1: A" or "Question 1: A"
# 4. "1: A" or "1 : (A)"
# 5. "(1) A" or "(1) - A"
ANSWER_ENTRY_PATTERNS = [
    # Q1: A or Question 1: A
    re.compile(r"(?:Q(?:uestion)?\.?\s*(\d+[a-zA-Z]?))\s*[:\.\-]\s*\(?([A-Da-d1-4]|True|False|[A-Za-z0-9\s]+?)\)?(?=(?:\s+Q|\n|\Z))", re.IGNORECASE),
    # 1-A or 1 - A
    re.compile(r"\b(\d+[a-zA-Z]?)\s*[-–]\s*\(?([A-Da-d1-4]|True|False)\)?", re.IGNORECASE),
    # 1. A or 1: A or 1) A
    re.compile(r"(?:^|\n|\s{2,})(\d+[a-zA-Z]?)\s*[\.\):]\s*\(?([A-Da-d1-4]|True|False)\)?(?=(?:\s{2,}|\n|\Z))", re.IGNORECASE),
]


class AnswerKeyDetector(AnswerKeyExtractorInterface):
    """Detects and parses answer keys from pages or dedicated answer key documents."""

    def extract_answers(
        self, pages: List[PageExtractionResult]
    ) -> List[DetectedAnswer]:
        """Extracts answer key mappings from all provided pages."""
        answers_dict: Dict[str, DetectedAnswer] = {}

        for page in pages:
            page_answers = self.extract_answers_from_text(
                page.text, source_page=page.page_number
            )
            for ans in page_answers:
                if ans.question_number not in answers_dict:
                    answers_dict[ans.question_number] = ans

        return list(answers_dict.values())

    def extract_answers_from_text(
        self, text: str, source_page: Optional[int] = None
    ) -> List[DetectedAnswer]:
        """Parses answer key entries from text string."""
        if not text:
            return []

        detected_answers: List[DetectedAnswer] = []

        for pattern in ANSWER_ENTRY_PATTERNS:
            matches = list(pattern.finditer(text))
            for m in matches:
                raw_q = m.group(1)
                raw_val = m.group(2).strip()

                norm_q = normalize_question_number(raw_q)
                norm_val = normalize_option_key(raw_val) if len(raw_val) <= 2 else raw_val

                confidence = 0.95
                matching_status = MatchingStatus.MATCHED

                detected_answers.append(
                    DetectedAnswer(
                        question_number=norm_q,
                        answer_value=norm_val,
                        answer_type="OPTION_KEY" if len(norm_val) == 1 else "TEXT",
                        confidence=confidence,
                        source_page=source_page,
                        matching_status=matching_status,
                    )
                )

        # De-duplicate by question number
        seen = {}
        unique_answers = []
        for ans in detected_answers:
            if ans.question_number not in seen:
                seen[ans.question_number] = True
                unique_answers.append(ans)

        return unique_answers
