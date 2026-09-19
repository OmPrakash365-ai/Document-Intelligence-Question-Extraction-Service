"""Image processor for standalone image documents (JPG, JPEG, PNG)."""

import os
from typing import List, Optional

from app.processors.interfaces import (
    DocumentParserInterface,
    PageExtractionResult,
    OCRProviderInterface,
)
from app.processors.image_preprocessor import ImagePreprocessor
from app.processors.ocr_processor import get_ocr_provider
from app.utils.text_utils import clean_text


class ImageProcessor(DocumentParserInterface):
    """Processes standalone images by running preprocessing and OCR."""

    def __init__(
        self,
        ocr_provider: Optional[OCRProviderInterface] = None,
        image_preprocessor: Optional[ImagePreprocessor] = None,
    ):
        self.ocr_provider = ocr_provider or get_ocr_provider()
        self.image_preprocessor = image_preprocessor or ImagePreprocessor()

    def extract_pages(
        self, file_path: str, output_image_dir: Optional[str] = None
    ) -> List[PageExtractionResult]:
        if output_image_dir:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            proc_img_path = os.path.join(output_image_dir, f"{base_name}_page_1.png")
        else:
            proc_img_path = f"/tmp/{os.path.basename(file_path)}_proc.png"

        # Preprocess
        self.image_preprocessor.preprocess(file_path, proc_img_path)

        # OCR
        ocr_result = self.ocr_provider.extract_text(proc_img_path)
        cleaned = clean_text(ocr_result.text)

        return [
            PageExtractionResult(
                page_number=1,
                text=cleaned,
                ocr_used=True,
                image_path=proc_img_path,
                confidence=ocr_result.confidence,
            )
        ]
