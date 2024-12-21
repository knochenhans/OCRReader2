from typing import List, Optional
import cv2
from loguru import logger
from papersize import SIZES, parse_length

from src.ocr_engine.ocr_box import (
    ImageBox,
    OCRBox,
    TextBox,
    HorizontalLine,
    VerticalLine,
)
from src.ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR
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
        self.paper_size = paper_size
        self.langs = langs
        self.layout = PageLayout([])
        self.image = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        self.layout.region = (0, 0, self.image.shape[1], self.image.shape[0])
        self.ppi = self.calculate_ppi()

    def calculate_ppi(self) -> int:
        # TODO: Let's assume 1:1 pixel ratio for now, so ignore width
        height_in = int(parse_length(SIZES[self.paper_size].split(" x ")[1], "in"))
        height_px = self.image.shape[0]
        return int(height_px / height_in)

    def analyze(self) -> None:
        layout_analyzer = LayoutAnalyzerTesserOCR(self.langs)

        self.layout.boxes = layout_analyzer.analyze_layout(
            self.image_path, self.ppi, self.layout.get_page_region()
        )
        self.layout.sort_boxes()

    def is_valid_box_index(self, box_index: int) -> bool:
        return box_index >= 0 and box_index < len(self.layout.boxes)

    def analyse_region(self, region: tuple[int, int, int, int]) -> List[OCRBox]:
        layout_analyzer = LayoutAnalyzerTesserOCR(self.langs)
        return layout_analyzer.analyze_layout(self.image_path, self.ppi, region)

    def analyze_box_(self, box_index: int) -> List[OCRBox]:
        if not self.is_valid_box_index(box_index):
            logger.error("Invalid box index: %d", box_index)
            return []

        region = self.layout.boxes[box_index]

        try:
            return self.analyse_region(
                (region.x, region.y, region.width, region.height)
            )
        except Exception as e:
            logger.error("Error analyzing layout for box at index %d: %s", box_index, e)
            return []

    def analyze_box(self, box_index: int) -> None:
        recognized_boxes = self.analyze_box_(box_index)

        if len(recognized_boxes) == 1:
            self.layout.boxes[box_index] = recognized_boxes[0]
        else:
            self.layout.remove_box(box_index)
            for recognized_box in recognized_boxes:
                self.layout.add_box(recognized_box)

    def align_box(self, box_index: int) -> None:
        recognized_boxes = self.analyze_box_(box_index)

        # if len(recognized_boxes) == 1:
        #     self.layout.boxes[box_index].x = recognized_boxes[0].x
        #     self.layout.boxes[box_index].y = recognized_boxes[0].y
        #     self.layout.boxes[box_index].width = recognized_boxes[0].width
        #     self.layout.boxes[box_index].height = recognized_boxes[0].height

        if len(recognized_boxes) > 0:
            # loop through all recognized boxes and find the box that is most similar to the original box
            best_box = None

            for recognized_box in recognized_boxes:
                if best_box is None:
                    best_box = recognized_box
                elif recognized_box.similarity(
                    self.layout.boxes[box_index]
                ) > best_box.similarity(self.layout.boxes[box_index]):
                    best_box = recognized_box

            if best_box is not None:
                self.layout.boxes[box_index].x = best_box.x
                self.layout.boxes[box_index].y = best_box.y
                self.layout.boxes[box_index].width = best_box.width
                self.layout.boxes[box_index].height = best_box.height
        else:
            self.layout.remove_box(box_index)

    def recognize_boxes(self) -> None:
        self.ocr_engine = OCREngineTesserOCR(self.langs)
        self.ocr_engine.recognize_boxes(self.image_path, self.ppi, self.layout.boxes)

    def generate_export_data(self) -> dict:
        export_data = {
            "page": {
                "ppi": self.ppi,
                "paper_size": self.paper_size,
            },
            "boxes": [],
        }

        for box in self.layout.boxes:
            export_data_entry = {
                "id": box.id,
                "position": box.position(),
                "class": box.class_,
                "tag": box.tag,
                "confidence": box.confidence,
            }

            match box:
                case TextBox():
                    export_data_entry["type"] = "text"
                    export_data_entry["text"] = box.text
                case ImageBox():
                    export_data_entry["type"] = "image"
                case HorizontalLine():
                    export_data_entry["type"] = "horizontal_line"
                case VerticalLine():
                    export_data_entry["type"] = "vertical_line"

            export_data["boxes"].append(export_data_entry)

        return export_data
