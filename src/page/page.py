from typing import List, Optional
import cv2
from loguru import logger
from iso639 import Lang


from src.page.page_settings import PageSettings
from project_settings import ProjectSettings
from src.page.ocr_box import (
    BoxType,
    ImageBox,
    OCRBox,
    TextBox,
    BOX_TYPE_MAP,
)
from src.page.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR
from src.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from src.page.page_layout import PageLayout


class Page:
    def __init__(
        self,
        image_path: str,
        order: int = 0,
    ) -> None:
        self.image_path = image_path
        self.order = order
        self.layout = PageLayout([])
        self.image = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
        self.layout.region = (0, 0, self.image.shape[1], self.image.shape[0])
        self.settings: PageSettings = PageSettings(ProjectSettings())

    def set_settings(self, project_settings: ProjectSettings) -> None:
        self.settings = PageSettings(project_settings)

    def analyze_page(self) -> None:
        langs = self.settings.get("langs") or ["eng"]
        layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        ppi = self.settings.get("ppi") or 300

        self.layout.boxes = layout_analyzer.analyze_layout(
            self.image_path, ppi, self.layout.get_page_region()
        )
        self.layout.sort_boxes()

    def is_valid_box_index(self, box_index: int) -> bool:
        return box_index >= 0 and box_index < len(self.layout.boxes)

    def analyse_region(self, region: tuple[int, int, int, int]) -> List[OCRBox]:
        langs = self.settings.get("langs") or ["eng"]
        ppi = self.settings.get("ppi") or 300
        layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        return layout_analyzer.analyze_layout(self.image_path, ppi, region)

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

        if len(recognized_boxes) > 0:
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
        langs = self.settings.get("langs") or ["eng"]
        ppi = self.settings.get("ppi") or 300
        self.ocr_engine = OCREngineTesserOCR(langs)
        self.ocr_engine.recognize_boxes(self.image_path, ppi, self.layout.boxes)

        # Convert empty TextBoxes to ImageBoxes
        for index, box in enumerate(self.layout.boxes):
            if isinstance(box, TextBox):
                if not box.text:
                    logger.info(f"Converting empty TextBox to ImageBox: {box}")
                    new_box = ImageBox(
                        box.x, box.y, box.width, box.height, BoxType.FLOWING_IMAGE
                    )
                    new_box.id = box.id
                    new_box.order = box.order
                    self.layout.boxes[index] = new_box

    def generate_export_data(self) -> dict:
        export_data = {
            "page": {
                "image_path": self.image_path,
                "order": self.order,
            },
            "boxes": [],
        }

        for box in self.layout.boxes:
            export_data_entry = {
                "id": box.id,
                "position": box.position(),
                "type": box.type,
                "class": box.class_,
                "tag": box.tag,
                "confidence": box.confidence,
                "ocr_results": box.ocr_results,
            }
            export_data["boxes"].append(export_data_entry)

        return export_data

    def to_dict(self) -> dict:
        data = {
            "page": {
                "image_path": self.image_path,
                "order": self.order,
                "layout": {
                    "boxes": [
                        box.to_dict() for box in self.layout.boxes if box is not None
                    ],
                    "region": self.layout.region,
                },
                "settings": self.settings.to_dict(),
            },
        }

        return data

    @classmethod
    def from_dict(cls, data: dict, project_settings: ProjectSettings) -> "Page":
        page_data = data["page"]

        page = cls(
            page_data["image_path"],
            order=page_data.get("order", 0),
        )

        for box_data in page_data["layout"]["boxes"]:
            box_type = box_data["type"]

            if box_type in BOX_TYPE_MAP:
                box = BOX_TYPE_MAP[box_type].from_dict(box_data)
            else:
                box = OCRBox.from_dict(box_data)

            page.layout.add_box(box)

        page.layout.region = tuple(page_data["layout"]["region"])
        page.settings = PageSettings.from_dict(page_data["settings"], project_settings)

        return page
