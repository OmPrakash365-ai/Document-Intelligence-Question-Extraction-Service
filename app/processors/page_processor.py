"""Page processor orchestrating document parsing based on file type."""

import os
from typing import List, Optional

from app.processors.interfaces import (
    DocumentParserInterface,
    PageExtractionResult,
    OCRProviderInterface,
)
from app.processors.pdf_processor import PDFProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.ocr_processor import get_ocr_provider
from app.processors.image_preprocessor import ImagePreprocessor
from app.core.exceptions import UnsupportedFileTypeError


class PageProcessor(DocumentParserInterface):
    """Factory and dispatcher for document parsing."""

    def __init__(
        self,
        ocr_provider: Optional[OCRProviderInterface] = None,
        image_preprocessor: Optional[ImagePreprocessor] = None,
    ):
        self.ocr_provider = ocr_provider or get_ocr_provider()
        self.image_preprocessor = image_preprocessor or ImagePreprocessor()
        self.pdf_processor = PDFProcessor(
            ocr_provider=self.ocr_provider,
            image_preprocessor=self.image_preprocessor,
        )
        self.image_processor = ImageProcessor(
            ocr_provider=self.ocr_provider,
            image_preprocessor=self.image_preprocessor,
        )

    def extract_pages(
        self, file_path: str, output_image_dir: Optional[str] = None
    ) -> List[PageExtractionResult]:
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        if ext == "pdf":
            return self.pdf_processor.extract_pages(file_path, output_image_dir)
        elif ext in ["jpg", "jpeg", "png"]:
            return self.image_processor.extract_pages(file_path, output_image_dir)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file format: {ext}")
