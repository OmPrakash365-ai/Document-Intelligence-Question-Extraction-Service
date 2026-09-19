"""Unit tests for answer key detector."""

from app.models.answer import MatchingStatus
from app.processors.answer_key_detector import AnswerKeyDetector
from app.processors.interfaces import PageExtractionResult


def test_answer_key_detection_dot_format():
    detector = AnswerKeyDetector()
    text = """
    Answer Key
    1. A
    2. C
    3. B
    4. D
    """
    answers = detector.extract_answers_from_text(text, source_page=1)
    assert len(answers) == 4
    assert answers[0].question_number == "1"
    assert answers[0].answer_value == "A"
    assert answers[1].question_number == "2"
    assert answers[1].answer_value == "C"


def test_answer_key_detection_dash_format():
    detector = AnswerKeyDetector()
    text = """
    Answers:
    1-B
    2-A
    3-D
    """
    answers = detector.extract_answers_from_text(text, source_page=2)
    assert len(answers) == 3
    assert answers[0].question_number == "1"
    assert answers[0].answer_value == "B"


def test_answer_key_detection_colon_format():
    detector = AnswerKeyDetector()
    text = """
    Q1: A
    Q2: C
    Q3: B
    """
    answers = detector.extract_answers_from_text(text, source_page=1)
    assert len(answers) == 3
    assert answers[0].question_number == "1"
    assert answers[0].answer_value == "A"
    assert answers[1].question_number == "2"
    assert answers[1].answer_value == "C"
