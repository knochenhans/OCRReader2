from typing import Dict, List, Optional, Tuple
from loguru import logger
from page.ocr_box import OCRBox, TextBox, BoxType  # type: ignore
from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR  # type: ignore
from ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR  # type: ignore
from settings import Settings  # type: ignore


class OCRProcessor:
    def __init__(self, settings: Optional[Settings] = None, langs: Optional[List[str]] = None, ppi: int = 300) -> None:
        self.ocr_engine = OCREngineTesserOCR(settings, langs)
        self.layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        self.ppi = ppi

    def recognize_boxes(self, image_path: str, boxes: List[OCRBox]) -> None:
        self.ocr_engine.recognize_boxes(image_path, self.ppi, boxes)
        logger.info(f"Recognized boxes: {boxes}")

    def analyze_layout(
        self, image_path: str, region: Tuple[int, int, int, int]
    ) -> List[OCRBox]:
        return self.layout_analyzer.analyze_layout(image_path, self.ppi, region)
