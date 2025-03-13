from typing import Optional
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import (
    QPixmap,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QWheelEvent,
    QImage,
    QColor,
)
from PySide6.QtCore import Qt, QPoint


class DraggableImageLabel(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.custom_pixmap: Optional[QPixmap] = None
        self.dragging: bool = False
        self.offset: QPoint = QPoint()
        self.image_offset: QPoint = QPoint(0, 0)
        self.scale_factor: float = 1.0

    def set_boxes(self, boxes: list) -> None:
        self.boxes = boxes

    def setPixmap(self, pixmap: QPixmap | QImage | str) -> None:
        if isinstance(pixmap, QImage):
            self.custom_pixmap = QPixmap.fromImage(pixmap)
        elif isinstance(pixmap, str):
            self.custom_pixmap = QPixmap(pixmap)
        else:
            self.custom_pixmap = pixmap
        self.image_offset = QPoint(0, 0)
        self.scale_factor = 1.0
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not isinstance(self.custom_pixmap, QPixmap):
            return

        # Draw the image
        painter = QPainter(self)
        scaled_pixmap = self.custom_pixmap.scaled(
            self.custom_pixmap.size() * self.scale_factor,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(QPoint(self.image_offset), scaled_pixmap)

        # Draw the word confidence boxes
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setOpacity(0.5)
        for box in self.boxes:
            # Boxes are tuples (x, y, width, height)
            painter.setBrush(QColor(*box[1]))
            x, y, width, height = box[0]
            painter.drawRect(
                int(x * self.scale_factor + self.image_offset.x()),
                int(y * self.scale_factor + self.image_offset.y()),
                int(width * self.scale_factor),
                int(height * self.scale_factor),
            )

        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.custom_pixmap is None:
            return

        if self.dragging:
            delta = event.position().toPoint() - self.offset
            self.image_offset += delta
            self.image_offset.setX(
                int(
                    max(
                        min(self.image_offset.x(), 0),
                        self.width() - self.custom_pixmap.width() * self.scale_factor,
                    )
                )
            )
            self.image_offset.setY(
                int(
                    max(
                        min(self.image_offset.y(), 0),
                        self.height() - self.custom_pixmap.height() * self.scale_factor,
                    )
                )
            )
            self.offset = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.custom_pixmap is None:
            return

        angle = event.angleDelta().y()
        factor = 1.02 if angle > 0 else 0.98
        new_scale_factor = self.scale_factor * factor

        if not self.custom_pixmap:
            return

        # Ensure the new scaled size is not smaller than a minimum size
        min_scale_factor = min(
            self.width() / self.custom_pixmap.width(),
            self.height() / self.custom_pixmap.height(),
        )
        if new_scale_factor >= min_scale_factor:
            self.scale_factor = new_scale_factor
            self.update()
