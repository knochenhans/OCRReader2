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

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.box_items: List[Tuple[QGraphicsRectItem, int]] = []
        self.pixmap_items: List[QGraphicsPixmapItem] = []

        self.scale_factor: float = 1.0

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def add_pixmaps(self, pixmaps: List[QPixmap]) -> None:
        self.clear_pixmaps()

        x_offset = 0
        for pixmap in pixmaps:
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setTransformationMode(
                Qt.TransformationMode.SmoothTransformation
            )
            pixmap_item.setPos(x_offset, 0)
            self._scene.addItem(pixmap_item)
            self.pixmap_items.append(pixmap_item)

            # Update the horizontal offset for the next pixmap
            x_offset += pixmap.width() + 10

        # Update the scene rect to fit all pixmaps
        self._scene.setSceneRect(
            0, 0, x_offset - 10, max(pixmap.height() for pixmap in pixmaps)
        )
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def clear_pixmaps(self) -> None:
        self._scene.clear()
        self.pixmap_items.clear()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_boxes(
        self, boxes: List[Tuple[Tuple[int, int, int, int], QColor]], image_index: int
    ) -> None:
        if image_index < 0 or image_index >= len(self.pixmap_items):
            raise ValueError("Invalid image index")

        pixmap_item = self.pixmap_items[image_index]
        pixmap_pos = pixmap_item.pos()  # Get the position of the pixmap

        for rect, color in boxes:
            x, y, width, height = rect
            box_item = QGraphicsRectItem(
                x + pixmap_pos.x(), y + pixmap_pos.y(), width, height
            )
            box_item.setBrush(color)
            box_item.setPen(QPen(Qt.PenStyle.NoPen))
            box_item.setOpacity(0.5)
            self._scene.addItem(box_item)
            self.box_items.append((box_item, image_index))

    def clear_boxes(self) -> None:
        for box_item, _ in self.box_items:
            self._scene.removeItem(box_item)
        self.box_items.clear()

    def wheelEvent(self, event: QWheelEvent) -> None:
        angle = event.angleDelta().y()
        factor = 1.05 if angle > 0 else 0.95
        self.scale(factor, factor)
        self.scale_factor *= factor

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.scale_factor = 1.0
        self.resetTransform()
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
