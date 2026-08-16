import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
from services.perception.screen import screen_perception
from tools.logger import log

RAPID_OCR_AVAILABLE = False
try:
    from rapidocr_onnxruntime import RapidOCR
    RAPID_OCR_AVAILABLE = True
except ImportError:
    RAPID_OCR_AVAILABLE = False


class OCREngineService:
    """
    Sub-30ms Local OCR Engine using RapidOCR ONNX Runtime.
    Extracts text from screenshots, UI elements, and documents offline.
    """
    def __init__(self):
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        if RAPID_OCR_AVAILABLE:
            try:
                log("🔍 Initializing RapidOCR ONNX Engine...")
                self.engine = RapidOCR()
                log("✅ RapidOCR Engine loaded successfully!")
            except Exception as e:
                log(f"⚠️ RapidOCR init error: {e}")
                self.engine = None

    def read_image_text(self, img_input: str | Path | Image.Image | np.ndarray) -> str:
        """
        Extracts all visible text from an image or screenshot.
        """
        if self.engine and RAPID_OCR_AVAILABLE:
            try:
                if isinstance(img_input, (str, Path)):
                    result, _ = self.engine(str(img_input))
                elif isinstance(img_input, Image.Image):
                    arr = np.array(img_input)
                    result, _ = self.engine(arr)
                else:
                    result, _ = self.engine(img_input)

                if result:
                    lines = [item[1] for item in result if item and len(item) > 1]
                    extracted = "\n".join(lines).strip()
                    log(f"🔍 OCR Extracted {len(lines)} lines of text.")
                    return extracted
            except Exception as e:
                log(f"RapidOCR processing error: {e}")

        log("ℹ️ OCR fallback: RapidOCR engine not loaded or returned empty.")
        return "No text extracted from screen."

    def read_screen_now(self) -> str:
        """
        Takes an instant screen capture and returns all readable text on screen.
        """
        img, _ = screen_perception.capture_screen_image("ocr_screen.png")
        return self.read_image_text(img)


# Global singleton instance
ocr_engine = OCREngineService()
