from typing import Dict

from OCRReader2.ocr_engine.layout_analyzer_cv2 import LayoutAnalyzerCV2
from OCRReader2.ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR

ANALYZER_REGISTRY: Dict[str, type] = {
    "cv2": LayoutAnalyzerCV2,
    "tesserocr": LayoutAnalyzerTesserOCR,
}
