"""Unit tests for multi-page question merger."""

from app.processors.question_merger import QuestionMerger
from app.processors.interfaces import DetectedQuestion, DetectedOption, PageExtractionResult
from app.models.question import QuestionType, ExtractionStatus


def test_merge_multipage_questions():
    merger = QuestionMerger()

    # Question 14 on page 1 (complete)
    q14 = DetectedQuestion(
        question_number="14",
        question_text="What protocol is used for secure web browsing?",
        question_type=QuestionType.MCQ,
        options=[
            DetectedOption(key="A", text="HTTP"),
            DetectedOption(key="B", text="HTTPS"),
        ],
        confidence=0.95,
        source_start_page=1,
        source_end_page=1,
    )

    # Question 15 start on page 1 (incomplete text, no options)
    q15_part1 = DetectedQuestion(
        question_number="15",
        question_text="Which of the following statements is correct regarding network security and",
        question_type=QuestionType.UNKNOWN,
        options=[],
        confidence=0.70,
        source_start_page=1,
        source_end_page=1,
    )

    # Question 15 continuation on page 2 (prompt conclusion + options)
    q15_part2 = DetectedQuestion(
        question_number="15",
        question_text="firewall architecture?",
        question_type=QuestionType.MCQ,
        options=[
            DetectedOption(key="A", text="Packet filtering happens at Layer 7."),
            DetectedOption(key="B", text="Stateful inspection tracks active connections."),
        ],
        confidence=0.85,
        source_start_page=2,
        source_end_page=2,
    )

    # Question 16 on page 2 (complete)
    q16 = DetectedQuestion(
        question_number="16",
        question_text="What is default port for DNS?",
        question_type=QuestionType.MCQ,
        options=[
            DetectedOption(key="A", text="53"),
            DetectedOption(key="B", text="80"),
        ],
        confidence=0.95,
        source_start_page=2,
        source_end_page=2,
    )

    pages = [
        PageExtractionResult(page_number=1, text="...", ocr_used=False),
        PageExtractionResult(page_number=2, text="...", ocr_used=False),
    ]

    raw_questions = [q14, q15_part1, q15_part2, q16]
    merged = merger.merge_multipage_questions(raw_questions, pages)

    assert len(merged) == 3
    assert merged[0].question_number == "14"
    assert merged[0].source_start_page == 1
    assert merged[0].source_end_page == 1

    # Merged Q15
    assert merged[1].question_number == "15"
    assert "network security and firewall architecture?" in merged[1].question_text
    assert len(merged[1].options) == 2
    assert merged[1].source_start_page == 1
    assert merged[1].source_end_page == 2

    # Q16
    assert merged[2].question_number == "16"
    assert merged[2].source_start_page == 2
    assert merged[2].source_end_page == 2
