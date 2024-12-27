from PySide6.QtGui import QBrush, QColor, QPen, Qt, QCursor, QPainter
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import QPointF, QRectF, QSizeF


class BoxItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)
        self.default_pen = QPen(QColor("black"), 1, Qt.PenStyle.SolidLine)
        self.selected_pen = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
        self.default_brush = QBrush(QColor(255, 255, 255, 0))  # Transparent
        self.selected_brush = QBrush(QColor(255, 0, 0, 50))  # Semi-transparent red

        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)

        self.setAcceptHoverEvents(True)

        self.set_movable(False)
        self.resizing = False
        self.resize_margin = 20
        self.handle_size = 6

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            self.setPen(self.selected_pen)
            self.setBrush(self.selected_brush)
        else:
            self.setPen(self.default_pen)
            self.setBrush(self.default_brush)

        super().paint(painter, option, widget)

        # Draw corner handles
        rect = self.rect()
        handle_brush = QBrush(QColor("blue"))
        handle_pen = QPen(QColor("blue"))

        painter.setBrush(handle_brush)
        painter.setPen(handle_pen)

        # Top-left handle
        painter.drawRect(
            QRectF(rect.topLeft(), QSizeF(self.handle_size, self.handle_size))
        )
        # Top-right handle
        painter.drawRect(
            QRectF(
                rect.topRight() - QPointF(self.handle_size, 0),
                QSizeF(self.handle_size, self.handle_size),
            )
        )
        # Bottom-left handle
        painter.drawRect(
            QRectF(
                rect.bottomLeft() - QPointF(0, self.handle_size),
                QSizeF(self.handle_size, self.handle_size),
            )
        )
        # Bottom-right handle
        painter.drawRect(
            QRectF(
                rect.bottomRight() - QPointF(self.handle_size, self.handle_size),
                QSizeF(self.handle_size, self.handle_size),
            )
        )

    def set_selected(self, selected):
        self.setSelected(selected)
        self.update()

    def set_movable(self, movable):
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.update()

    def hoverMoveEvent(self, event):
        pos = event.pos()
        rect = self.rect()
        if (
            rect.left() + self.resize_margin
            >= pos.x()
            >= rect.left() - self.resize_margin
            and rect.top() + self.resize_margin
            >= pos.y()
            >= rect.top() - self.resize_margin
        ):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        elif (
            rect.right() - self.resize_margin
            <= pos.x()
            <= rect.right() + self.resize_margin
            and rect.top() + self.resize_margin
            >= pos.y()
            >= rect.top() - self.resize_margin
        ):
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        elif (
            rect.left() + self.resize_margin
            >= pos.x()
            >= rect.left() - self.resize_margin
            and rect.bottom() - self.resize_margin
            <= pos.y()
            <= rect.bottom() + self.resize_margin
        ):
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        elif (
            rect.right() - self.resize_margin
            <= pos.x()
            <= rect.right() + self.resize_margin
            and rect.bottom() - self.resize_margin
            <= pos.y()
            <= rect.bottom() + self.resize_margin
        ):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        pos = event.pos()
        rect = self.rect()
        if (
            rect.left() + self.resize_margin
            >= pos.x()
            >= rect.left() - self.resize_margin
            and rect.top() + self.resize_margin
            >= pos.y()
            >= rect.top() - self.resize_margin
        ):
            self.resizing = True
            self.resize_corner = "top_left"
        elif (
            rect.right() - self.resize_margin
            <= pos.x()
            <= rect.right() + self.resize_margin
            and rect.top() + self.resize_margin
            >= pos.y()
            >= rect.top() - self.resize_margin
        ):
            self.resizing = True
            self.resize_corner = "top_right"
        elif (
            rect.left() + self.resize_margin
            >= pos.x()
            >= rect.left() - self.resize_margin
            and rect.bottom() - self.resize_margin
            <= pos.y()
            <= rect.bottom() + self.resize_margin
        ):
            self.resizing = True
            self.resize_corner = "bottom_left"
        elif (
            rect.right() - self.resize_margin
            <= pos.x()
            <= rect.right() + self.resize_margin
            and rect.bottom() - self.resize_margin
            <= pos.y()
            <= rect.bottom() + self.resize_margin
        ):
            self.resizing = True
            self.resize_corner = "bottom_right"
        else:
            self.set_movable(True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            pos = event.pos()
            rect = self.rect()
            if self.resize_corner == "top_left":
                rect.setTopLeft(pos)
            elif self.resize_corner == "top_right":
                rect.setTopRight(pos)
            elif self.resize_corner == "bottom_left":
                rect.setBottomLeft(pos)
            elif self.resize_corner == "bottom_right":
                rect.setBottomRight(pos)
            self.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.set_movable(False)
        super().mouseReleaseEvent(event)
