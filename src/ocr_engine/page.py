from typing import List, Optional
import cv2
from papersize import SIZES, parse_length

from src.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from src.ocr_engine.page_layout import PageLayout


class Page:
    def __init__(
        self,
        image_path: str,
        paper_size: str = "a4",
        langs: List = [str],
    ) -> None:
        self.image_path = image_path
        self.layout = PageLayout([])
        self.paper_size = paper_size
        self.ppi = self.calculate_ppi()
        self.langs = langs

    def calculate_ppi(self) -> int:
        # TODO: Let's assume 1:1 pixel ratio for now, so ignore width
        height_in = int(parse_length(SIZES[self.paper_size].split(" x ")[1], "in"))
        image = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        height_px = image.shape[0]
        return int(height_px / height_in)

    def analyze_layout(self) -> None:
        self.layout.analyze_layout(self.image_path, self.ppi, self.langs)

    def recognize_boxes(self) -> None:
        self.ocr_engine = OCREngineTesserOCR(self.langs)
        self.ocr_engine.recognize_boxes_threaded(self.image_path, self.ppi, self.layout.boxes)