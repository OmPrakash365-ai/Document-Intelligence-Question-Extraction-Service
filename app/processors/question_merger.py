"""Multi-page question merger to unify questions spanning page boundaries."""

import re
import logging
from typing import List
from app.processors.interfaces import DetectedQuestion, PageExtractionResult
from app.models.question import QuestionType, ExtractionStatus
from app.processors.option_detector import OptionDetector

logger = logging.getLogger("document_intelligence")


class QuestionMerger:
    """Detects and merges questions that span across page breaks."""

    def __init__(self, option_detector: OptionDetector = None):
        self.option_detector = option_detector or OptionDetector()

    def merge_multipage_questions(
        self,
        questions: List[DetectedQuestion],
        pages: List[PageExtractionResult],
    ) -> List[DetectedQuestion]:
        """
        Scans questions across page boundaries and unifies questions that were split.
        """
        if not questions:
            return questions

        merged: List[DetectedQuestion] = []
        i = 0
        while i < len(questions):
            curr = questions[i]

            # Check if there is a next question candidate
            if i + 1 < len(questions):
                next_q = questions[i + 1]

                # Check if next question is on the immediate subsequent page
                if next_q.source_start_page == curr.source_end_page + 1:
                    # Signals that curr question was interrupted:
                    # 1. curr question has no options, but next_q has options and very little/no question prompt
                    # 2. curr text ends without terminal punctuation (ends with 'and', 'the', 'of', or comma)
                    # 3. next_q has identical question number, or no distinct question number
                    curr_stripped = curr.question_text.strip()
                    is_curr_incomplete = False

                    if curr_stripped and curr_stripped[-1] not in "?.:!":
                        is_curr_incomplete = True
                    if any(
                        curr_stripped.lower().endswith(w)
                        for w in [" of", " the", " that", " and", " which", " is", " are", ","]
                    ):
                        is_curr_incomplete = True
                    if not curr.options and next_q.options and len(next_q.question_text.strip()) < 80:
                        is_curr_incomplete = True

                    if is_curr_incomplete:
                        logger.info(
                            f"Merging multi-page question {curr.question_number} spanning page "
                            f"{curr.source_start_page} to {next_q.source_end_page}"
                        )
                        # Merge text
                        combined_text = f"{curr.question_text} {next_q.question_text}".strip()
                        # Re-detect options across combined text if needed
                        combined_options = curr.options + next_q.options
                        if not combined_options:
                            combined_text, combined_options = self.option_detector.detect_options(
                                combined_text
                            )

                        # Create merged question
                        merged_q = DetectedQuestion(
                            question_number=curr.question_number,
                            question_text=combined_text,
                            question_type=curr.question_type
                            if curr.question_type != QuestionType.UNKNOWN
                            else next_q.question_type,
                            options=combined_options,
                            confidence=round((curr.confidence + next_q.confidence) / 2.0, 2),
                            source_start_page=curr.source_start_page,
                            source_end_page=next_q.source_end_page,
                            extraction_status=ExtractionStatus.SUCCESS,
                            review_issues=curr.review_issues + next_q.review_issues,
                        )

                        # If merge had borderline signals, record a review item
                        if not curr.options and not next_q.options:
                            merged_q.review_issues.append(
                                {
                                    "issue_type": "MULTI_PAGE_MERGE_UNCERTAIN",
                                    "severity": "LOW",
                                    "description": f"Question {curr.question_number} was merged across pages "
                                    f"{curr.source_start_page} and {next_q.source_end_page}.",
                                }
                            )

                        merged.append(merged_q)
                        i += 2  # skip next_q since it was merged
                        continue

            merged.append(curr)
            i += 1

        return merged
