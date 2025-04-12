from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
)


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # Initialize the scene and pixmap item
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.box_items: List[QGraphicsRectItem] = []

        self.scale_factor: float = 1.0

        # Configure the view
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.pixmap_item = QGraphicsPixmapItem(QPixmap())
        self.pixmap_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self._scene.addItem(self.pixmap_item)

    def setPixmap(self, pixmap: QPixmap) -> None:
        self.pixmap_item.setPixmap(pixmap)

        self.resetTransform()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def set_boxes(self, boxes: List[Tuple[Tuple[int, int, int, int], QColor]]) -> None:
        # Remove existing box items
        for box_item in self.box_items:
            self._scene.removeItem(box_item)
        self.box_items.clear()

        # Add new box items
        for box, color in boxes:
            x, y, width, height = box
            rect_item = QGraphicsRectItem(x, y, width, height)
            rect_item.setBrush(color)
            rect_item.setPen(QPen(Qt.PenStyle.NoPen))
            rect_item.setOpacity(0.5)
            self._scene.addItem(rect_item)
            self.box_items.append(rect_item)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.pixmap_item is None:
            return

        angle = event.angleDelta().y()
        factor = 1.05 if angle > 0 else 0.95
        self.scale(factor, factor)
        self.scale_factor *= factor

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.pixmap_item is not None:
            self.scale_factor = 1.0
            self.resetTransform()
            self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
