"""OCR processor using Tesseract with mock fallback."""

import logging
import os
import shutil
from typing import Optional
from PIL import Image
import pytesseract

from app.core.config import get_settings
from app.processors.interfaces import OCRProviderInterface, OCRResult

logger = logging.getLogger("document_intelligence")
settings = get_settings()


class TesseractOCRProvider(OCRProviderInterface):
    """Tesseract OCR implementation."""

    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract_text(self, image_path: str) -> OCRResult:
        try:
            image = Image.open(image_path)
            # Extract detailed data with bounding boxes and confidence
            data = pytesseract.image_to_data(
                image, lang=self.lang, output_type=pytesseract.Output.DICT
            )

            text_parts = []
            confidences = []
            word_boxes = []

            n_boxes = len(data["text"])
            for i in range(n_boxes):
                word = data["text"][i].strip()
                conf = float(data["conf"][i])

                if word:
                    text_parts.append(word)
                    if conf >= 0:  # -1 indicates background / line header
                        confidences.append(conf)
                        word_boxes.append(
                            {
                                "text": word,
                                "left": data["left"][i],
                                "top": data["top"][i],
                                "width": data["width"][i],
                                "height": data["height"][i],
                                "confidence": conf / 100.0,
                            }
                        )

            full_text = pytesseract.image_to_string(image, lang=self.lang).strip()

            # Normalize average confidence between 0.0 and 1.0
            avg_conf = (
                (sum(confidences) / len(confidences) / 100.0) if confidences else 0.8
            )

            return OCRResult(
                text=full_text,
                confidence=round(min(1.0, max(0.0, avg_conf)), 2),
                word_boxes=word_boxes,
                raw_data=data,
            )
        except Exception as e:
            logger.error(f"Tesseract OCR error on {image_path}: {str(e)}")
            raise e


class MockOCRProvider(OCRProviderInterface):
    """Deterministic Mock OCR provider for environments without Tesseract binary or unit tests."""

    def __init__(self, default_confidence: float = 0.95):
        self.default_confidence = default_confidence

    def extract_text(self, image_path: str) -> OCRResult:
        # Check if there's a sidecar text file or return default
        base_path = os.path.splitext(image_path)[0]
        sidecar = f"{base_path}.txt"
        text = ""
        if os.path.exists(sidecar):
            with open(sidecar, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "Mock OCR extracted text for testing purposes."

        return OCRResult(
            text=text,
            confidence=self.default_confidence,
            word_boxes=[],
        )


def get_ocr_provider(provider_type: Optional[str] = None) -> OCRProviderInterface:
    """Factory to get the configured OCR provider, falling back to mock if tesseract is missing."""
    p_type = provider_type or settings.OCR_PROVIDER
    if p_type == "mock":
        return MockOCRProvider()

    # Check if tesseract binary exists in PATH
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        return TesseractOCRProvider(lang=settings.OCR_LANGUAGE)

    logger.warning(
        "Tesseract binary not found in PATH. Using MockOCRProvider as fallback."
    )
    return MockOCRProvider()
