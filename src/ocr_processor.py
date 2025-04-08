from typing import Dict, List, Optional, Tuple

from loguru import logger

from ocr_engine.analyzer_registry import ANALYZER_REGISTRY
from ocr_engine.layout_analyzer import LayoutAnalyzer
from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from page.ocr_box import OCRBox
from settings.settings import Settings


class OCRProcessor:
    def __init__(self, project_settings: Optional[Settings] = None) -> None:
        self.ocr_engine = OCREngineTesserOCR(project_settings)
        self.project_settings = project_settings

        # Dynamically initialize available analyzers using the registry
        self.analyzers: Dict[str, LayoutAnalyzer] = {
            analyzer_id: analyzer_class(project_settings)
            for analyzer_id, analyzer_class in ANALYZER_REGISTRY.items()
        }

    def recognize_boxes(self, image_path: str, boxes: List[OCRBox]) -> None:
        self.ocr_engine.recognize_boxes(image_path, boxes)
        logger.info(f"Recognized boxes: {boxes}")

    def analyze_layout(
        self, image_path: str, region: Tuple[int, int, int, int]
    ) -> List[OCRBox]:
        if self.project_settings is None:
            logger.warning("Project settings are not provided. Using default settings.")
            self.project_settings = Settings()

        # Get the default analyzer from project_settings or fallback to CV2
        default_analyzer = self.project_settings.get("layout_analyzer")
        self.current_analyzer_id: str = default_analyzer
        analyzer = self.analyzers[self.current_analyzer_id]
        return analyzer.analyze_layout(image_path, region)
