from typing import Optional, Dict
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap
from loguru import logger

from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page.ocr_box import OCRBox  # type: ignore
from page.box_type_color_map import BOX_TYPE_COLOR_MAP  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore


class PageEditorScene(QGraphicsScene):
    def __init__(self, controller: Optional[PageEditorController] = None) -> None:
        super().__init__()
        self.controller = controller
        self.boxes: Dict[str, BoxItem] = {}
        self.page_image_item: Optional[QGraphicsItem] = None

    def add_box_item_from_ocr_box(self, box: OCRBox) -> None:
        box_item = BoxItem(box.id, 0, 0, box.width, box.height)
        box_item.set_color(BOX_TYPE_COLOR_MAP[box.type])

        if self.controller:
            box_item.box_moved.connect(self.on_box_item_moved)
            box_item.box_resized.connect(self.on_box_item_resized)
            box_item.box_right_clicked.connect(self.on_box_item_right_clicked)

        self.addItem(box_item)
        box_item.setPos(box.x, box.y)
        self.boxes[box.id] = box_item

    def remove_box_item(self, box_id: str) -> None:
        if box_id in self.boxes:
            self.removeItem(self.boxes[box_id])
            del self.boxes[box_id]

    def on_box_item_moved(self, box_id: str, pos: QPointF) -> None:
        if self.controller:
            logger.debug(f"Page box item {box_id} moved to {pos}")
            ocr_box = self.controller.page.layout.get_ocr_box_by_id(box_id)
            if ocr_box:
                ocr_box.update_position(int(pos.x()), int(pos.y()), "GUI")

    def on_box_item_resized(self, box_id: str, pos: QPointF, size: QPointF) -> None:
        if self.controller:
            logger.debug(f"Page box item {box_id} resized by relative position {pos} and size {size}")
            ocr_box = self.controller.page.layout.get_ocr_box_by_id(box_id)
            if ocr_box:
                box_item = self.boxes[box_id]

                new_x = int(box_item.pos().x() + pos.x())
                new_y = int(box_item.pos().y() + pos.y())
                new_width = int(size.x())
                new_height = int(size.y())

                ocr_box.update_position(new_x, new_y, "GUI")
                ocr_box.update_size(new_width, new_height, "GUI")

    def on_box_item_right_clicked(self, box_id: str) -> None:
        # Get all currently selected items
        selected_items = self.selectedItems()

        # Add the clicked item to the selection if it is not already selected
        if box_id not in [
            item.box_id for item in selected_items if isinstance(item, BoxItem)
        ]:
            selected_items.append(self.boxes[box_id])

        # Get ids of all selected boxes
        selected_box_ids = [
            item.box_id for item in selected_items if isinstance(item, BoxItem)
        ]
        if self.controller:
            self.controller.show_context_menu(selected_box_ids)

    def set_page_image(self, page_pixmap: QPixmap) -> None:
        if self.page_image_item:
            self.removeItem(self.page_image_item)

        self.page_image_item = QGraphicsPixmapItem(page_pixmap)
        self.page_image_item.setZValue(-1)
        self.page_image_item.setCacheMode(
            QGraphicsPixmapItem.CacheMode.DeviceCoordinateCache
        )
        self.page_image_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self.addItem(self.page_image_item)
