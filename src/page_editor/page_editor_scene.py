from typing import Optional
from PySide6.QtCore import Qt, QRectF, QRect
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap, QPainter

from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page.ocr_box import OCRBox  # type: ignore


class PageEditorScene(QGraphicsScene):
    def __init__(self, controller: Optional[PageEditorController] = None) -> None:
        super().__init__()
        self.controller = controller
        self.boxes: dict[str, QGraphicsRectItem] = {}
        self.page_image_item: Optional[QGraphicsItem] = None

    def add_box(self, box: OCRBox) -> None:
        rect_item = QGraphicsRectItem(box.x, box.y, box.width, box.height)
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.addItem(rect_item)
        self.boxes[box.id] = rect_item

    def set_page_image(self, page_pixmap: QPixmap) -> None:
        if self.page_image_item:
            self.removeItem(self.page_image_item)

        self.page_image_item = QGraphicsPixmapItem(page_pixmap)
        self.page_image_item.setZValue(-1)
        self.addItem(self.page_image_item)
