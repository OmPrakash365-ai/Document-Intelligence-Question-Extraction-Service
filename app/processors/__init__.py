"""Processors package."""

from app.processors.interfaces import (
    OCRResult,
    PageExtractionResult,
    DetectedOption,
    DetectedQuestion,
    DetectedAnswer,
    OCRProviderInterface,
    DocumentParserInterface,
    QuestionExtractorInterface,
    AnswerKeyExtractorInterface,
    DocumentUnderstandingProvider,
)
from app.processors.image_preprocessor import ImagePreprocessor
from app.processors.ocr_processor import (
    TesseractOCRProvider,
    MockOCRProvider,
    get_ocr_provider,
)
from app.processors.pdf_processor import PDFProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.page_processor import PageProcessor
from app.processors.option_detector import OptionDetector
from app.processors.question_detector import QuestionDetector
from app.processors.question_merger import QuestionMerger
from app.processors.answer_key_detector import AnswerKeyDetector

__all__ = [
    "OCRResult",
    "PageExtractionResult",
    "DetectedOption",
    "DetectedQuestion",
    "DetectedAnswer",
    "OCRProviderInterface",
    "DocumentParserInterface",
    "QuestionExtractorInterface",
    "AnswerKeyExtractorInterface",
    "DocumentUnderstandingProvider",
    "ImagePreprocessor",
    "TesseractOCRProvider",
    "MockOCRProvider",
    "get_ocr_provider",
    "PDFProcessor",
    "ImageProcessor",
    "PageProcessor",
    "OptionDetector",
    "QuestionDetector",
    "QuestionMerger",
    "AnswerKeyDetector",
]
