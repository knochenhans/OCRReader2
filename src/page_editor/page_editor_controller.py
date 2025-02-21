from typing import Any, List, Optional

from loguru import logger
from page.page import Page  # type: ignore
from iso639 import Lang

from PySide6.QtGui import QPixmap, QAction, QCursor
from PySide6.QtWidgets import QMenu

from page.ocr_box import OCRBox, TextBox  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore
from page.box_type_color_map import BOX_TYPE_COLOR_MAP  # type: ignore
from src.line_break_editor.ocr_edit_dialog import OCREditDialog  # type: ignore
from page.box_type import BoxType  # type: ignore


class PageEditorController:
    def __init__(self, page: Page, scene):
        self.page: Page = page
        self.scene = scene
        self.delete_box_action: Optional[QAction] = None
        self.add_box_action: Optional[QAction] = None

        self.create_actions()
        self.context_menu = self.create_context_menu()

    def load_page(self) -> None:
        self.scene.set_page_image(QPixmap(self.page.image_path))

        for box in self.page.layout.ocr_boxes:
            self.add_page_box_item_from_ocr_box(box)

    def create_actions(self) -> None:
        self.align_boxes_action = QAction("Align", None)
        self.align_boxes_action.triggered.connect(self.align_boxes)

        self.analyze_boxes_action = QAction("Analyze", None)
        self.analyze_boxes_action.triggered.connect(self.analyze_boxes)

        self.remove_line_breaks_action = QAction("Remove Line Breaks", None)
        self.remove_line_breaks_action.triggered.connect(self.remove_line_breaks)

    def align_boxes(self) -> None:
        # self.page.align_box()
        # for box in self.page.layout.boxes:
        #     self.on_ocr_box_updated(box, "Backend")
        pass

    def analyze_boxes(self) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box_index = self.page.layout.get_ocr_box_index_by_id(ocr_box_id)

            if ocr_box_index is not None:
                self.page.analyze_ocr_box(ocr_box_index)

    def remove_line_breaks(self, all: bool = False) -> None:
        selected_boxes: List[BoxItem]
        if all:
            selected_boxes = self.scene.get_all_box_items()
        else:
            selected_boxes = self.scene.get_selected_box_items()

        langs = self.page.settings.get("langs")
        if langs:
            language = langs[0]
            lang_pt1 = Lang(language).pt1

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box_index = self.page.layout.get_ocr_box_index_by_id(ocr_box_id)

            if ocr_box_index is not None:
                ocr_box = self.page.layout.ocr_boxes[ocr_box_index]
                if ocr_box.type in [
                    BoxType.FLOWING_TEXT,
                    BoxType.HEADING_TEXT,
                    BoxType.CAPTION_TEXT,
                    BoxType.PULLOUT_TEXT,
                ]:
                    if isinstance(ocr_box, TextBox):
                        line_break_dialog = OCREditDialog(ocr_box, lang_pt1)
                        line_break_dialog.exec()

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
            box_item: BoxItem = self.scene.boxes.get(ocr_box.id)
            if box_item:
                box_item.setPos(ocr_box.x, ocr_box.y)
                box_item.setRect(0, 0, ocr_box.width, ocr_box.height)
                box_item.set_color(BOX_TYPE_COLOR_MAP[ocr_box.type])
                logger.info(f"Updated box {ocr_box.id} via {source}")

    # def recognize_text(self, box_id: int) -> str:
    #     box = self.page.layout.boxes[box_id]
    #     # text = box.recognize_text()
    #     return ""

    def create_context_menu(self) -> QMenu:
        context_menu = QMenu()
        if self.align_boxes_action:
            context_menu.addAction(self.align_boxes_action)
        if self.analyze_boxes_action:
            context_menu.addAction(self.analyze_boxes_action)
        if self.remove_line_breaks_action:
            context_menu.addAction(self.remove_line_breaks_action)
        return context_menu

    def show_context_menu(self, box_ids: List[str]) -> None:
        cursor_pos = QCursor.pos()
        self.context_menu.exec_(cursor_pos)
