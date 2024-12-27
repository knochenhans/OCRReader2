from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap

from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page.ocr_box import OCRBox  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore


class PageEditorScene(QGraphicsScene):
    def __init__(self, controller: Optional[PageEditorController] = None) -> None:
        super().__init__()
        self.controller = controller
        self.boxes: dict[str, BoxItem] = {}
        self.page_image_item: Optional[QGraphicsItem] = None

    def add_box(self, box: OCRBox) -> None:
        box_item = BoxItem(box.x, box.y, box.width, box.height)

        self.addItem(box_item)
        self.boxes[box.id] = box_item

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
