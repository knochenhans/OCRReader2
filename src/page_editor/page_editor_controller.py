from typing import Any, List, Optional

from loguru import logger
from page.page import Page  # type: ignore

from PySide6.QtGui import QPixmap, QAction, QCursor
from PySide6.QtWidgets import QMenu, QGraphicsScene

from ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR  # type: ignore
from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR  # type: ignore
from page.box_type import BoxType  # type: ignore
from page.ocr_box import OCRBox  # type: ignore


class PageEditorController:
    def __init__(self, page: Page, scene):
        self.page: Page = page
        self.scene = scene
        self.delete_box_action: Optional[QAction] = None
        self.add_box_action: Optional[QAction] = None

        self.create_actions()

    def load_page(self) -> None:
        self.scene.set_page_image(QPixmap(self.page.image_path))

        for box in self.page.layout.ocr_boxes:
            self.add_page_box_item_from_ocr_box(box)

    def create_actions(self) -> None:
        self.align_boxes_action = QAction("Align Boxes", None)
        self.align_boxes_action.triggered.connect(self.align_boxes)

    def align_boxes(self) -> None:
        # self.page.layout.align_boxes()
        # for box in self.page.layout.boxes:
        #     self.on_ocr_box_updated(box, "Backend")
        pass

    def add_new_box(self, box: OCRBox) -> None:
        self.page.layout.add_ocr_box(box)
        self.add_page_box_item_from_ocr_box(box)
        logger.info(f"Added new box {box.id}")

    def add_page_box_item_from_ocr_box(self, box: OCRBox) -> None:
        logger.info(f"Added box {box.id}")
        self.scene.add_box_item_from_ocr_box(box)
        box.add_callback(self.on_ocr_box_updated)

    def remove_box(self, box_id: str) -> None:
        self.page.layout.remove_box_by_id(box_id)
        self.scene.remove_box_item(box_id)
        logger.info(f"Removed box {box_id}")

    def on_ocr_box_updated(self, ocr_box: OCRBox, source: Optional[str] = None) -> None:
        if self.scene and source != "Backend":
            box_item = self.scene.boxes.get(ocr_box.id)
            if box_item:
                box_item.setRect(ocr_box.x, ocr_box.y, ocr_box.width, ocr_box.height)
                logger.info(f"Updated box {ocr_box.id} via {source}")

    # def recognize_text(self, box_id: int) -> str:
    #     box = self.page.layout.boxes[box_id]
    #     # text = box.recognize_text()
    #     return ""

    def get_context_menu(self) -> QMenu:
        context_menu = QMenu()
        if self.align_boxes_action:
            context_menu.addAction(self.align_boxes_action)
        return context_menu

    def show_context_menu(self, box_ids: List[str]) -> None:
        context_menu = self.get_context_menu()
        cursor_pos = QCursor.pos()
        context_menu.exec_(cursor_pos)
