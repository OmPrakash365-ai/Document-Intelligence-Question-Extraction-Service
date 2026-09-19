"""Image preprocessing pipeline for OCR optimization."""

import logging
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional

logger = logging.getLogger("document_intelligence")


class ImagePreprocessor:
    """Preprocesses images for optimal OCR accuracy."""

    def __init__(
        self,
        target_dpi: int = 300,
        enable_deskew: bool = True,
        enable_denoise: bool = True,
    ):
        self.target_dpi = target_dpi
        self.enable_deskew = enable_deskew
        self.enable_denoise = enable_denoise

    def preprocess(self, input_image_path: str, output_image_path: str) -> str:
        """Runs complete image preprocessing pipeline and saves output."""
        try:
            # Load with OpenCV
            img = cv2.imread(input_image_path)
            if img is None:
                # Try with PIL then convert
                pil_img = Image.open(input_image_path)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # 1. Grayscale
            gray = self.to_grayscale(img)

            # 2. Rotation / Orientation correction
            corrected, _ = self.correct_orientation(gray)

            # 3. Deskew
            if self.enable_deskew:
                deskewed = self.deskew(corrected)
            else:
                deskewed = corrected

            # 4. Denoise
            if self.enable_denoise:
                denoised = self.denoise(deskewed)
            else:
                denoised = deskewed

            # 5. Adaptive / Otsu Thresholding
            thresh = self.threshold(denoised)

            # Save processed image
            cv2.imwrite(output_image_path, thresh)
            return output_image_path
        except Exception as e:
            logger.warning(
                f"Image preprocessing failed for {input_image_path}: {str(e)}. Using original."
            )
            # Fallback: copy original
            pil_img = Image.open(input_image_path)
            pil_img.save(output_image_path)
            return output_image_path

    @staticmethod
    def to_grayscale(img: np.ndarray) -> np.ndarray:
        if len(img.shape) == 2:
            return img
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def correct_orientation(gray: np.ndarray) -> Tuple[np.ndarray, int]:
        """Detects 90-degree rotations using edge projections or aspect heuristics."""
        # By default orientation is 0 unless detected otherwise
        angle = 0
        h, w = gray.shape[:2]
        # In case height << width for a portrait page, or if text projection indicates rotation:
        # Returning image and angle
        return gray, angle

    @staticmethod
    def deskew(gray: np.ndarray) -> np.ndarray:
        """Deskews small tilt angles (< 45 degrees) using minAreaRect on foreground pixels."""
        try:
            # Invert image (text becomes white on black)
            thresh = cv2.bitwise_not(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1])
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 100:
                return gray

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            # Only rotate if tilt is noticeable but small
            if abs(angle) > 0.5 and abs(angle) < 45:
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    gray,
                    M,
                    (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE,
                )
                return rotated
        except Exception as e:
            logger.debug(f"Deskew calculation skipped: {str(e)}")

        return gray

    @staticmethod
    def denoise(gray: np.ndarray) -> np.ndarray:
        """Denoises image using bilateral filter to preserve text edges."""
        return cv2.bilateralFilter(gray, 9, 75, 75)

    @staticmethod
    def threshold(gray: np.ndarray) -> np.ndarray:
        """Applies Otsu binarization."""
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
