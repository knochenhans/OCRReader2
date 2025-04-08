from ocr_engine.layout_analyzer_cv2 import LayoutAnalyzerCV2
from ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR

ANALYZER_REGISTRY = {
    "cv2": LayoutAnalyzerCV2,
    "tesserocr": LayoutAnalyzerTesserOCR,
}
