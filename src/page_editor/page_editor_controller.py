from typing import Any, Callable, List, Optional, Tuple

from loguru import logger
from page.page import Page  # type: ignore
from iso639 import Lang

from PySide6.QtGui import QPixmap, QAction, QCursor
from PySide6.QtWidgets import QMenu, QInputDialog

from page.ocr_box import OCRBox, TextBox  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore
from page.box_type_color_map import BOX_TYPE_COLOR_MAP  # type: ignore
from ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog  # type: ignore
from page.box_type import BoxType  # type: ignore
from page_editor.header_footer_item import HEADER_FOOTER_ITEM_TYPE  # type: ignore
from settings import Settings  # type: ignore


class PageEditorController:
    def __init__(
        self,
        page: Page,
        scene,
        application_settings: Optional[Settings] = None,
        project_settings: Optional[Settings] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> None:
        self.page: Page = page
        self.scene = scene
        self.application_settings = application_settings
        self.project_settings = project_settings
        self.progress_callback = progress_callback

        self.delete_box_action: Optional[QAction] = None
        self.add_box_action: Optional[QAction] = None

        self.create_actions()
        # self.context_menu = self.create_context_menu()

    def open_page(self) -> None:
        if self.page.image_path:
            self.scene.set_page_image(QPixmap(self.page.image_path))

        if self.page.layout.header_y > 0:
            self.scene.add_header_footer(
                HEADER_FOOTER_ITEM_TYPE.HEADER, self.page.layout.header_y
            )
        if self.page.layout.footer_y > 0:
            self.scene.add_header_footer(
                HEADER_FOOTER_ITEM_TYPE.FOOTER, self.page.layout.footer_y
            )

        for box in self.page.layout.ocr_boxes:
            self.add_box_item_from_ocr_box(box)

    def create_actions(self) -> None:
        self.align_boxes_action = QAction("Align", None)
        self.align_boxes_action.triggered.connect(self.align_boxes)

        self.analyze_boxes_action = QAction("Analyze", None)
        self.analyze_boxes_action.triggered.connect(self.analyze_boxes)

        self.recognize_text_action = QAction("Recognize Text", None)
        self.recognize_text_action.triggered.connect(self.recognize_text)

        self.ocr_editor_action = QAction("Remove Line Breaks", None)
        self.ocr_editor_action.triggered.connect(self.ocr_editor)

        self.add_header_action = QAction("Add Header", None)
        self.add_header_action.triggered.connect(self.start_set_header)

        self.add_footer_action = QAction("Add Footer", None)
        self.add_footer_action.triggered.connect(self.start_set_footer)

        self.renumber_box_action = QAction("Renumber Box", None)
        self.renumber_box_action.triggered.connect(self.renumber_box)

        self.start_box_flow_selection_action = QAction("Start Box Flow Selection", None)
        self.start_box_flow_selection_action.triggered.connect(
            self.start_box_flow_selection
        )

        self.set_box_flow_action = QAction("Set Box Flow", None)
        self.set_box_flow_action.triggered.connect(lambda: self.toggle_box_flow(None))

        self.remove_box_flow_action = QAction("Remove Box Flow", None)
        self.remove_box_flow_action.triggered.connect(self.remove_box_flow)

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
                self.on_ocr_box_updated(
                    self.page.layout.ocr_boxes[ocr_box_index], "Backend"
                )

    def analyze_region(self, region: Tuple[int, int, int, int]) -> None:
        for ocr_box in self.page.analyze_page(region, True):
            self.add_box_item_from_ocr_box(ocr_box)

        for box in self.page.layout.ocr_boxes:
            self.on_ocr_box_updated(box, "GUI")

    def recognize_text(self) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box_index = self.page.layout.get_ocr_box_index_by_id(ocr_box_id)

            if ocr_box_index is not None:
                self.page.recognize_ocr_boxes(
                    ocr_box_index, False, self.progress_callback
                )
                # self.on_ocr_box_updated(
                #     self.page.layout.ocr_boxes[ocr_box_index], "GUI"
                # )

    def ocr_editor(self, box_id: str = "") -> None:
        if self.project_settings:
            langs = self.project_settings.get("langs")
            if langs and self.application_settings:
                ocr_edit_dialog = OCREditorDialog(
                    [self.page],
                    Lang(langs[0]).pt1,
                    self.application_settings,
                    box_id,
                )
                ocr_edit_dialog.exec()

    def add_box(
        self, region: Tuple[int, int, int, int], box_type: BoxType, order: int
    ) -> None:
        if not self.scene:
            return

        self.page.layout.add_new_ocr_box(region, box_type, order)
        index = len(self.page.layout.ocr_boxes) - 1
        self.on_ocr_box_updated(self.page.layout.ocr_boxes[index], "GUI")

    def add_box_item_from_ocr_box(self, box: OCRBox) -> None:
        self.scene.add_box_item_from_ocr_box(box)
        box.add_callback(self.on_ocr_box_updated)
        self.page.layout.sort_ocr_boxes_by_order()
        logger.info(f"Added box {box.id}")

    def remove_box(self, box_id: str) -> None:
        ocr_box = self.page.layout.get_ocr_box_by_id(box_id)
        if ocr_box:
            ocr_box.clear_callbacks()

        self.page.layout.remove_ocr_box_by_id(box_id)
        self.scene.remove_box_item(box_id)
        self.page.layout.sort_ocr_boxes_by_order()
        logger.info(f"Removed box {box_id}")

    def on_ocr_box_updated(self, ocr_box: OCRBox, source: Optional[str] = None) -> None:
        if self.scene and source != "Backend":
            box_item: BoxItem = self.scene.boxes.get(ocr_box.id)
            if box_item:
                box_item.setPos(ocr_box.x, ocr_box.y)
                box_item.setRect(0, 0, ocr_box.width, ocr_box.height)
                box_item.set_color(BOX_TYPE_COLOR_MAP[ocr_box.type])
                box_item.order = ocr_box.order + 1

                if isinstance(ocr_box, TextBox):
                    box_item.is_recognized = ocr_box.has_text()
                    box_item.has_user_text = ocr_box.user_text.strip() != ""
                    box_item.flows_into_next = ocr_box.flows_into_next
                    box_item.has_user_data = ocr_box.user_data != {}

                box_item.update()
                self.scene.update()
                logger.info(f"Updated box {ocr_box.id} via {source}")
            else:
                logger.warning(f"Box {ocr_box.id} not found in scene, adding it")
                self.add_box_item_from_ocr_box(ocr_box)

    def renumber_box(self) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box_index = self.page.layout.get_ocr_box_index_by_id(ocr_box_id)

            if ocr_box_index is not None:
                current_number = ocr_box_index + 1
                new_number, ok = QInputDialog.getInt(
                    self.scene.views()[0],
                    "Renumber Box",
                    "Enter new number:",
                    current_number,
                )
                if ok:
                    self.page.layout.change_box_index(ocr_box_index, new_number - 1)
                    self.page.layout.sort_ocr_boxes_by_order()

        for box in self.page.layout.ocr_boxes:
            self.on_ocr_box_updated(box, "GUI")

    def create_context_menu(self, box_items: Optional[List[BoxItem]]) -> QMenu:
        context_menu = QMenu()

        if box_items:
            ocr_box = (
                self.page.layout.get_ocr_box_by_id(box_items[0].box_id)
                if box_items
                else None
            )

            if ocr_box:
                context_menu.addAction(f"Box ID: {ocr_box.id}")
                context_menu.addAction(f"Box Type: {ocr_box.type}")

                box_types = [box_type.name for box_type in BoxType]

                # Add box type actions as sub-menu
                box_type_menu = context_menu.addMenu("Change Box Type")
                for box_type in box_types:
                    box_type_action = box_type_menu.addAction(box_type)

                    # Connect the box type action to the change_box_type method
                    box_type_action.triggered.connect(
                        lambda _, box_id=ocr_box.id, box_type=box_type: self.change_box_type(
                            box_id, BoxType[box_type]
                        )
                    )

                # Show recognized text if available
                if isinstance(ocr_box, TextBox):
                    text_menu = context_menu.addMenu("Recognized Text")
                    text_menu.addAction(ocr_box.get_text())

                context_menu.addSeparator()
                self.construct_box_context_menu(context_menu)
        else:
            context_menu = self.construct_page_context_menu()
        return context_menu

    def construct_page_context_menu(self) -> QMenu:
        context_menu = QMenu()

        if self.add_box_action:
            context_menu.addAction(self.add_box_action)
        if self.add_header_action:
            context_menu.addAction(self.add_header_action)
        if self.add_footer_action:
            context_menu.addAction(self.add_footer_action)
        if self.start_box_flow_selection_action:
            context_menu.addAction(self.start_box_flow_selection_action)

        return context_menu

    def construct_box_context_menu(self, context_menu: QMenu) -> QMenu:
        if self.align_boxes_action:
            context_menu.addAction(self.align_boxes_action)
        if self.analyze_boxes_action:
            context_menu.addAction(self.analyze_boxes_action)
        if self.recognize_text_action:
            context_menu.addAction(self.recognize_text_action)
        if self.ocr_editor_action:
            context_menu.addAction(self.ocr_editor_action)
        if self.renumber_box_action:
            context_menu.addAction(self.renumber_box_action)
        if self.set_box_flow_action:
            context_menu.addAction(self.set_box_flow_action)
        if self.remove_box_flow_action:
            context_menu.addAction(self.remove_box_flow_action)

        return context_menu

    def change_box_type(self, box_id: str, box_type: BoxType) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box = self.page.layout.get_ocr_box_by_id(ocr_box_id)
            if ocr_box:
                ocr_box = ocr_box.convert_to(box_type)
                self.page.layout.replace_ocr_box_by_id(ocr_box_id, ocr_box)
                self.on_ocr_box_updated(ocr_box, "GUI")

    def show_context_menu(self, box_items: Optional[List[BoxItem]] = None) -> None:
        cursor_pos = QCursor.pos()
        self.context_menu = self.create_context_menu(box_items)
        self.context_menu.exec(cursor_pos)

    def start_set_header(self) -> None:
        self.scene.views()[0].set_header()

    def start_set_footer(self) -> None:
        self.scene.views()[0].set_footer()

    def set_header(self, y: int) -> None:
        self.page.layout.header_y = y
        logger.info(f"Set header to {y}")

    def set_footer(self, y: int) -> None:
        self.page.layout.footer_y = y
        logger.info(f"Set footer to {y}")

    def start_box_flow_selection(self) -> None:
        self.scene.views()[0].start_box_flow_selection()

    def toggle_box_flow(self, box_items: Optional[List[BoxItem]] = None) -> None:
        if not box_items:
            box_items = self.scene.get_selected_box_items()

        if not box_items:
            return

        box_items.sort(key=lambda box_item: box_item.order)
        for i, box_item in enumerate(box_items):
            ocr_box = self.page.layout.get_ocr_box_by_id(box_item.box_id)
            if ocr_box and isinstance(ocr_box, TextBox):
                ocr_box.flows_into_next = not ocr_box.flows_into_next
                self.on_ocr_box_updated(ocr_box, "GUI")
                logger.info(
                    f"Toggled box flow for {ocr_box.id} to {ocr_box.flows_into_next}"
                )

    def remove_box_flow(self) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        for selected_box in selected_boxes:
            ocr_box_id = selected_box.box_id
            ocr_box = self.page.layout.get_ocr_box_by_id(ocr_box_id)
            if ocr_box:
                if isinstance(ocr_box, TextBox):
                    ocr_box.flows_into_next = False
                    self.on_ocr_box_updated(ocr_box, "GUI")
                    logger.info(f"Removed box flow for {ocr_box.id}")

    def add_custom_user_data(self, box_id: str, key: str, value: Any) -> None:
        ocr_box = self.page.layout.get_ocr_box_by_id(box_id)
        if ocr_box:
            ocr_box.add_user_data(key, value)
            self.on_ocr_box_updated(ocr_box, "GUI")

    def merge_selected_boxes(self) -> None:
        selected_boxes: List[BoxItem] = self.scene.get_selected_box_items()

        if len(selected_boxes) < 2:
            return

        selected_boxes.sort(key=lambda box_item: box_item.order)
        original_box_id = selected_boxes[0].box_id
        original_ocr_box = self.page.layout.get_ocr_box_by_id(original_box_id)

        if not original_ocr_box:
            return

        for other_box_item in selected_boxes[1:]:
            other_ocr_box = self.page.layout.get_ocr_box_by_id(other_box_item.box_id)
            if other_ocr_box:
                original_ocr_box_index = self.page.layout.get_ocr_box_index_by_id(
                    original_box_id
                )
                other_ocr_box_index = self.page.layout.get_ocr_box_index_by_id(
                    other_box_item.box_id
                )
                if (
                    original_ocr_box_index is not None
                    and other_ocr_box_index is not None
                ):
                    self.page.merge_ocr_box_with_ocr_box(
                        original_ocr_box_index, other_ocr_box_index
                    )
                    self.scene.remove_box_item(other_ocr_box.id)
                self.scene.remove_box_item(other_ocr_box.id)

    def clear_boxes_callbacks(self) -> None:
        for box_item in self.scene.boxes.values():
            ocr_box = self.page.layout.get_ocr_box_by_id(box_item.box_id)
            if ocr_box:
                ocr_box.clear_callbacks()

    def split_y_ocr_box(self, box_id: str, split_y: int) -> None:
        ocr_box = self.page.layout.get_ocr_box_by_id(box_id)
        if ocr_box:
            new_box = self.page.layout.split_y_ocr_box(ocr_box.id, split_y)
            self.on_ocr_box_updated(ocr_box, "GUI")

            if new_box:
                self.add_box_item_from_ocr_box(new_box)

    def on_box_double_clicked(self, box_id: str) -> None:
        self.ocr_editor(box_id)

    def has_box_items(self) -> bool:
        return len(self.scene.boxes) > 0

    def clear_box_items(self) -> None:
        self.scene.clear_box_items()
        self.page.layout.clear_ocr_boxes()
        logger.info("Cleared box items")
