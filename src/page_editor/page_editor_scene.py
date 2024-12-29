from typing import Optional, Dict
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap

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

    def add_box(self, box: OCRBox) -> None:
        box_item = BoxItem(box.id, 0, 0, box.width, box.height)
        box_item.set_color(BOX_TYPE_COLOR_MAP[box.type])

        if self.controller:
            box_item.box_moved.connect(self.on_box_moved)
            box_item.box_resized.connect(self.on_box_resized)

        self.addItem(box_item)
        box_item.setPos(box.x, box.y)
        self.boxes[box.id] = box_item

    def remove_box(self, box_id: str) -> None:
        if box_id in self.boxes:
            self.removeItem(self.boxes[box_id])
            del self.boxes[box_id]

    def on_box_moved(self, box_id: str, pos: QPointF) -> None:
        if self.controller:
            ocr_box = self.controller.page.layout.get_box_by_id(box_id)
            if ocr_box:
                ocr_box.update_position(int(pos.x()), int(pos.y()), "GUI")

    def on_box_resized(
        self, box_id: str, x: int, y: int, width: int, height: int
    ) -> None:
        if self.controller:
            ocr_box = self.controller.page.layout.get_box_by_id(box_id)
            if ocr_box:
                ocr_box.update_size(width, height, "GUI")

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
