from typing import Callable, Dict, List, Optional, Tuple

from loguru import logger
from SettingsManager import SettingsManager

from OCRReader2.ocr_engine.analyzer_registry import ANALYZER_REGISTRY
from OCRReader2.ocr_engine.layout_analyzer import LayoutAnalyzer
from OCRReader2.ocr_engine.ocr_engine import OCREngine
from OCRReader2.ocr_engine.ocr_engine_batch_server import OCREngineBatchServer
from OCRReader2.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from OCRReader2.page.ocr_box import OCRBox


class OCRProcessor:
    def __init__(self, project_settings: Optional[SettingsManager] = None) -> None:
        self.ocr_engine = OCREngineTesserOCR(project_settings)
        self.project_settings = project_settings

        # Dynamically initialize available analyzers using the registry
        self.analyzers: Dict[str, LayoutAnalyzer] = {
            analyzer_id: analyzer_class(project_settings)
            for analyzer_id, analyzer_class in ANALYZER_REGISTRY.items()
        }

    def recognize_boxes(
        self,
        image_path: str,
        boxes: List[OCRBox],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> None:
        self.ocr_engine.recognize_boxes(image_path, boxes, progress_callback)
        logger.info(f"Recognized boxes: {boxes}")

    def analyze_layout(
        self, image_path: str, region: Tuple[int, int, int, int]
    ) -> List[OCRBox]:
        if self.project_settings is None:
            logger.warning("Project settings are not provided. Using default settings.")
            self.project_settings = SettingsManager("project_settings")

            return []
        # Get the default analyzer from project_settings or fallback to CV2
        default_analyzer = self.project_settings.get("layout_analyzer")
        self.current_analyzer_id: str = default_analyzer
        analyzer = self.analyzers[self.current_analyzer_id]
        return analyzer.analyze_layout(image_path, region)
