"""Abstract interfaces and data transfer objects for document processing pipeline."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from app.models.question import QuestionType, ExtractionStatus
from app.models.answer import MatchingStatus


@dataclass
class OCRResult:
    text: str
    confidence: float
    word_boxes: List[Dict[str, Any]] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class PageExtractionResult:
    page_number: int
    text: str
    ocr_used: bool
    image_path: Optional[str] = None
    confidence: float = 1.0


@dataclass
class DetectedOption:
    key: str
    text: str
    confidence: float = 1.0


@dataclass
class DetectedQuestion:
    question_number: str
    question_text: str
    question_type: QuestionType
    options: List[DetectedOption] = field(default_factory=list)
    confidence: float = 0.0
    source_start_page: int = 1
    source_end_page: int = 1
    extraction_status: ExtractionStatus = ExtractionStatus.SUCCESS
    review_issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DetectedAnswer:
    question_number: str
    answer_value: str
    answer_type: str = "OPTION_KEY"
    confidence: float = 0.0
    source_page: Optional[int] = None
    source_document_id: Optional[str] = None
    matching_status: MatchingStatus = MatchingStatus.UNMATCHED


class OCRProviderInterface(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> OCRResult:
        """Extracts text and confidence from an image file."""
        pass


class DocumentParserInterface(ABC):
    @abstractmethod
    def extract_pages(
        self, file_path: str, output_image_dir: Optional[str] = None
    ) -> List[PageExtractionResult]:
        """Extracts page text and optional images from a document."""
        pass


class QuestionExtractorInterface(ABC):
    @abstractmethod
    def extract_questions(
        self, pages: List[PageExtractionResult]
    ) -> List[DetectedQuestion]:
        """Detects and extracts questions across all pages."""
        pass


class AnswerKeyExtractorInterface(ABC):
    @abstractmethod
    def extract_answers(
        self, pages: List[PageExtractionResult]
    ) -> List[DetectedAnswer]:
        """Detects and extracts answer keys from pages."""
        pass


class DocumentUnderstandingProvider(ABC):
    """Abstraction for optional external vision/LLM model with fallback."""

    @abstractmethod
    def extract_questions(
        self, document_path: str, pages: List[PageExtractionResult]
    ) -> List[DetectedQuestion]:
        pass

    @abstractmethod
    def extract_answer_key(
        self, document_path: str, pages: List[PageExtractionResult]
    ) -> List[DetectedAnswer]:
        pass
