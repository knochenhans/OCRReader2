from typing import List, Optional
import cv2  # type: ignore
import numpy as np  # type: ignore
from loguru import logger


from page.page_settings import PageSettings  # type: ignore
from project.project_settings import ProjectSettings  # type: ignore
from page.ocr_box import (  # type: ignore
    OCRBox,
    TextBox,
    BOX_TYPE_MAP,
)
from page.box_type import BoxType  # type: ignore
from ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR  # type: ignore
from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR  # type: ignore
from page.page_layout import PageLayout  # type: ignore


class Page:
    def __init__(
        self,
        image_path: Optional[str] = None,
        order: int = 0,
    ) -> None:
        self.image_path = image_path
        self.order = order
        self.layout = PageLayout([])
        self.image: Optional[np.ndarray] = None

        if self.image_path:
            self.image = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)

            if self.image is None:
                logger.error("Error loading image: %s", self.image_path)
                return
            else:
                self.layout.region = (0, 0, self.image.shape[1], self.image.shape[0])
        self.settings: PageSettings = PageSettings(ProjectSettings())

    def set_settings(self, project_settings: ProjectSettings) -> None:
        self.settings = PageSettings(project_settings)

    def analyze_page(
        self,
        region: Optional[tuple[int, int, int, int]] = None,
        keep_existing_boxes: bool = False,
    ) -> List[OCRBox]:
        if not self.image_path:
            logger.error("No image path set for page")
            return []

        langs = self.settings.get("langs") or ["eng"]
        layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        ppi = self.settings.get("ppi") or 300

        if self.image is None:
            return []

        if region is None:
            region = self.layout.get_page_region()

        ocr_boxes = layout_analyzer.analyze_layout(self.image_path, ppi, region)

        # Get new order numbers for the boxes
        max_order = max([box.order for box in self.layout.ocr_boxes], default=-1)
        for box in ocr_boxes:
            max_order += 1
            box.order = max_order

        if keep_existing_boxes:
            self.layout.ocr_boxes += ocr_boxes
        else:
            self.layout.ocr_boxes = ocr_boxes
        self.layout.sort_ocr_boxes()
        return ocr_boxes

    def is_valid_box_index(self, box_index: int) -> bool:
        return box_index >= 0 and box_index < len(self.layout.ocr_boxes)

    def analyze_region(self, region: tuple[int, int, int, int]) -> List[OCRBox]:
        if not self.image_path:
            logger.error("No image path set for page")
            return []

        langs = self.settings.get("langs") or ["eng"]
        ppi = self.settings.get("ppi") or 300
        layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        return layout_analyzer.analyze_layout(self.image_path, ppi, region)

    def analyze_ocr_box_(self, box_index: int) -> List[OCRBox]:
        if not self.is_valid_box_index(box_index):
            logger.error("Invalid ocr_box index: %d", box_index)
            return []

        region = self.layout.ocr_boxes[box_index]

        try:
            return self.analyze_region(
                (region.x, region.y, region.width, region.height)
            )
        except Exception as e:
            logger.error(
                "Error analyzing layout for ocr_box at index %d: %s", box_index, e
            )
            return []

    def analyze_ocr_box(self, ocr_box_index: int) -> None:
        recognized_boxes = self.analyze_ocr_box_(ocr_box_index)

        if len(recognized_boxes) == 1:
            # Keep some data from the original box
            recognized_boxes[0].id = self.layout.ocr_boxes[ocr_box_index].id
            recognized_boxes[0].order = self.layout.ocr_boxes[ocr_box_index].order
            recognized_boxes[0]._callbacks = self.layout.ocr_boxes[
                ocr_box_index
            ]._callbacks
            recognized_boxes[0].tag = self.layout.ocr_boxes[ocr_box_index].tag
            recognized_boxes[0].class_ = self.layout.ocr_boxes[ocr_box_index].class_
            self.layout.ocr_boxes[ocr_box_index] = recognized_boxes[0]
            recognized_boxes[0].notify_callbacks("Backend")
        else:
            self.layout.remove_ocr_box(ocr_box_index)
            for recognized_box in recognized_boxes:
                self.layout.add_ocr_box(recognized_box)

    def align_ocr_box(self, ocr_box_index: int) -> None:
        recognized_boxes = self.analyze_ocr_box_(ocr_box_index)

        if len(recognized_boxes) > 0:
            best_box = None

            for recognized_box in recognized_boxes:
                if best_box is None:
                    best_box = recognized_box
                elif recognized_box.similarity(
                    self.layout.ocr_boxes[ocr_box_index]
                ) > best_box.similarity(self.layout.ocr_boxes[ocr_box_index]):
                    best_box = recognized_box

            if best_box is not None:
                self.layout.ocr_boxes[ocr_box_index].x = best_box.x
                self.layout.ocr_boxes[ocr_box_index].y = best_box.y
                self.layout.ocr_boxes[ocr_box_index].width = best_box.width
                self.layout.ocr_boxes[ocr_box_index].height = best_box.height
        else:
            self.layout.remove_ocr_box(ocr_box_index)

    def recognize_ocr_boxes(
        self, box_index: Optional[int] = None, convert_empty_textboxes: bool = True
    ) -> None:
        if not self.image_path:
            logger.error("No image path set for page")
            return

        langs = self.settings.get("langs") or ["eng"]
        ppi = self.settings.get("ppi") or 300
        self.ocr_engine = OCREngineTesserOCR(langs)

        if box_index is not None:
            if not self.is_valid_box_index(box_index):
                logger.error("Invalid ocr_box index: %d", box_index)
                return

            boxes_to_recognize = [self.layout.ocr_boxes[box_index]]
        else:
            boxes_to_recognize = self.layout.ocr_boxes

        self.ocr_engine.recognize_boxes(self.image_path, ppi, boxes_to_recognize)

        logger.info(f"Recognized boxes: {boxes_to_recognize}")

        if convert_empty_textboxes and box_index is None:
            # Convert empty TextBoxes to ImageBoxes
            for i, ocr_box in enumerate(self.layout.ocr_boxes):
                if isinstance(ocr_box, TextBox):
                    if not ocr_box.has_text():
                        self.convert_ocr_box(i, BoxType.FLOWING_IMAGE)

        # Notify callbacks for recognized boxes
        for ocr_box in boxes_to_recognize:
            ocr_box.notify_callbacks("Backend")

    def convert_ocr_box(self, box_index: int, box_type: BoxType) -> None:
        if not self.is_valid_box_index(box_index):
            logger.error("Invalid ocr_box index: %d", box_index)
            return

        ocr_box = self.layout.ocr_boxes[box_index]
        new_box = ocr_box.convert_to(box_type)
        self.layout.ocr_boxes[box_index] = new_box

    def generate_page_export_data(self) -> dict:
        langs = self.settings.get("langs") or ["eng"]

        export_data = {
            "image_path": self.image_path,
            "order": self.order,
            "lang": langs[0],
            "boxes": [],
        }

        for ocr_box in self.layout.ocr_boxes:
            export_data_entry = {
                "id": ocr_box.id,
                "order": ocr_box.order,
                "position": ocr_box.position(),
                "type": ocr_box.type,
                "class": ocr_box.class_,
                "tag": ocr_box.tag,
                "confidence": ocr_box.confidence,
                "ocr_results": ocr_box.ocr_results,
            }

            if isinstance(ocr_box, TextBox):
                export_data_entry["user_text"] = ocr_box.user_text

            export_data["boxes"].append(export_data_entry)

        return export_data

    def set_header(self, header: int) -> None:
        self.layout.header_y = header

    def set_footer(self, footer: int) -> None:
        self.layout.footer_y = footer

    def to_dict(self) -> dict:
        data = {
            "page": {
                "image_path": self.image_path,
                "order": self.order,
                "layout": self.layout.to_dict(),
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
                ocr_box = BOX_TYPE_MAP[box_type].from_dict(box_data)
            else:
                ocr_box = OCRBox.from_dict(box_data)

            page.layout.add_ocr_box(ocr_box)

        page.layout.region = tuple(page_data["layout"]["region"])
        page.layout.header_y = page_data["layout"].get("header_y", 0)
        page.layout.footer_y = page_data["layout"].get("footer_y", 0)
        page.settings = PageSettings.from_dict(page_data["settings"], project_settings)

        return page
