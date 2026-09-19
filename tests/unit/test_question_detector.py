"""Unit tests for question detector and option detector."""

from app.models.question import QuestionType
from app.processors.option_detector import OptionDetector
from app.processors.question_detector import QuestionDetector
from app.processors.interfaces import PageExtractionResult


def test_option_detector_alphabetic_lines():
    detector = OptionDetector()
    text = """What is the capital of France?
A. London
B. Berlin
C. Paris
D. Rome"""

    q_text, options = detector.detect_options(text)
    assert q_text == "What is the capital of France?"
    assert len(options) == 4
    assert options[0].key == "A"
    assert options[0].text == "London"
    assert options[2].key == "C"
    assert options[2].text == "Paris"


def test_option_detector_parenthesized():
    detector = OptionDetector()
    text = """Which protocol is used for email transfer? (a) HTTP (b) SMTP (c) FTP (d) SSH"""
    q_text, options = detector.detect_options(text)
    assert len(options) == 4
    assert options[0].key == "A"
    assert options[1].key == "B"
    assert options[1].text == "SMTP"


def test_question_classifier():
    detector = QuestionDetector()

    # True / False
    q_tf = detector.classify_question_type("Python is a compiled language. True or False?", [])
    assert q_tf == QuestionType.TRUE_FALSE

    # Fill in the blank
    q_fitb = detector.classify_question_type("The speed of light in vacuum is _____ m/s.", [])
    assert q_fitb == QuestionType.FILL_IN_THE_BLANK

    # MCQ
    detector_opt = OptionDetector()
    _, opts = detector_opt.detect_options("A. Opt1\nB. Opt2\nC. Opt3\nD. Opt4")
    q_mcq = detector.classify_question_type("Which element is a noble gas?", opts)
    assert q_mcq == QuestionType.MCQ

    # Multiple Select
    q_ms = detector.classify_question_type("Select all that apply for sorting algorithms:", opts)
    assert q_ms == QuestionType.MULTIPLE_SELECT

    # Descriptive
    q_desc = detector.classify_question_type("Explain in detail the Paxos consensus algorithm.", [])
    assert q_desc == QuestionType.DESCRIPTIVE

    # Short Answer
    q_sa = detector.classify_question_type("What is an operating system?", [])
    assert q_sa == QuestionType.SHORT_ANSWER


def test_question_extraction_from_page():
    detector = QuestionDetector()
    page_text = """
    Examination Paper 2026
    
    1. Which data structure is FIFO?
    A. Stack
    B. Queue
    C. Tree
    D. Graph
    
    Q2. What is Python?
    A. Snake
    B. Language
    
    Question 3: Explain polymorphism with an example.
    """
    page = PageExtractionResult(page_number=1, text=page_text, ocr_used=False)
    questions = detector.extract_questions_from_page(page)

    assert len(questions) == 3
    assert questions[0].question_number == "1"
    assert questions[0].question_type == QuestionType.MCQ
    assert len(questions[0].options) == 4

    assert questions[1].question_number == "2"
    assert len(questions[1].options) == 2

    assert questions[2].question_number == "3"
    assert questions[2].question_type in [QuestionType.SHORT_ANSWER, QuestionType.DESCRIPTIVE]
