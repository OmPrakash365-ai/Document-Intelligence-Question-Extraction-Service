"""PDF processor using PyMuPDF (fitz) with automatic OCR detection."""

import logging
import os
from typing import List, Optional
import fitz  # PyMuPDF

from app.core.config import get_settings
from app.processors.interfaces import (
    DocumentParserInterface,
    PageExtractionResult,
    OCRProviderInterface,
)
from app.processors.image_preprocessor import ImagePreprocessor
from app.processors.ocr_processor import get_ocr_provider
from app.utils.text_utils import clean_text

logger = logging.getLogger("document_intelligence")
settings = get_settings()


class PDFProcessor(DocumentParserInterface):
    """Processes digital and scanned PDFs with smart OCR fallback."""

    def __init__(
        self,
        ocr_provider: Optional[OCRProviderInterface] = None,
        image_preprocessor: Optional[ImagePreprocessor] = None,
        dpi: int = 300,
    ):
        self.ocr_provider = ocr_provider or get_ocr_provider()
        self.image_preprocessor = image_preprocessor or ImagePreprocessor(target_dpi=dpi)
        self.dpi = dpi

    def _is_native_text_sufficient(self, text: str) -> bool:
        """Determines if native PDF text is of sufficient quality without requiring OCR."""
        cleaned = clean_text(text)
        if len(cleaned) < 40:
            return False

        # Check character distribution (avoid garbled font encoding)
        words = cleaned.split()
        if len(words) < 5:
            return False

        # Ratio of alphanumeric characters
        alnum_count = sum(1 for c in cleaned if c.isalnum())
        if alnum_count / len(cleaned) < 0.4:
            return False

        return True

    def extract_pages(
        self, file_path: str, output_image_dir: Optional[str] = None
    ) -> List[PageExtractionResult]:
        doc = fitz.open(file_path)
        results: List[PageExtractionResult] = []

        for page_idx in range(len(doc)):
            page_num = page_idx + 1
            page = doc[page_idx]

            # 1. Try native digital text extraction
            native_text = page.get_text()

            if self._is_native_text_sufficient(native_text):
                cleaned = clean_text(native_text)
                results.append(
                    PageExtractionResult(
                        page_number=page_num,
                        text=cleaned,
                        ocr_used=False,
                        image_path=None,
                        confidence=0.98,
                    )
                )
            else:
                # 2. Render page as high-resolution image for OCR
                zoom = self.dpi / 72.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # Determine storage path
                if output_image_dir:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    raw_img_path = os.path.join(
                        output_image_dir, f"{base_name}_page_{page_num}_raw.png"
                    )
                    proc_img_path = os.path.join(
                        output_image_dir, f"{base_name}_page_{page_num}.png"
                    )
                else:
                    raw_img_path = f"/tmp/page_{page_num}_raw.png"
                    proc_img_path = f"/tmp/page_{page_num}.png"

                pix.save(raw_img_path)

                # Preprocess image
                self.image_preprocessor.preprocess(raw_img_path, proc_img_path)
                if os.path.exists(raw_img_path) and raw_img_path != proc_img_path:
                    try:
                        os.remove(raw_img_path)
                    except OSError:
                        pass

                # Run OCR
                ocr_result = self.ocr_provider.extract_text(proc_img_path)
                cleaned = clean_text(ocr_result.text)

                results.append(
                    PageExtractionResult(
                        page_number=page_num,
                        text=cleaned,
                        ocr_used=True,
                        image_path=proc_img_path,
                        confidence=ocr_result.confidence,
                    )
                )

        doc.close()
        return results
