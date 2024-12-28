from enum import Enum
from typing import Any, Optional

from PySide6.QtGui import QBrush, QColor, QPen, Qt, QCursor, QPainter
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsItem,
    QWidget,
    QStyleOptionGraphicsItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PySide6.QtCore import QPointF, QRectF, QSizeF, QEvent, Signal, QObject


class BoxItemState(Enum):
    DEFAULT = 1
    SELECTED = 2


class BoxItem(QGraphicsRectItem, QObject):
    box_moved = Signal(str, int, int)
    box_resized = Signal(str, int, int, int, int)

    def __init__(
        self,
        id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        QGraphicsRectItem.__init__(self, x, y, width, height, parent)
        QObject.__init__(self)
        self.set_color((0, 0, 0))

        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True
        )

        self.setAcceptHoverEvents(True)

        self.box_id = id
        self.resizing = False
        self.resize_margin = 20
        self.handle_size = 6

        self.set_movable(False)

    def update_pens_and_brushes(self) -> None:
        self.border_pens = {
            BoxItemState.DEFAULT: QPen(self.color, 1, Qt.PenStyle.SolidLine),
            BoxItemState.SELECTED: QPen(self.color, 2, Qt.PenStyle.DashLine),
        }
        self.default_brush = QBrush(self.color)
        self.default_brush.setStyle(Qt.BrushStyle.SolidPattern)

        self.default_brush.setColor(self.color)
        default_color = QColor(self.color)
        default_color.setAlphaF(0.1)
        self.default_brush.setColor(default_color)  # 10% opacity

        self.selected_brush = QBrush(self.color)
        selected_color = QColor(self.color)
        selected_color.setAlphaF(0.25)
        self.selected_brush.setColor(selected_color)  # 25% opacity

    def set_color(self, color: tuple[int, int, int]) -> None:
        self.color = QColor(*color)
        self.update_pens_and_brushes()
        self.update()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        if self.isSelected():
            self.setPen(self.border_pens[BoxItemState.SELECTED])
            self.setBrush(self.selected_brush)
        else:
            self.setPen(self.border_pens[BoxItemState.DEFAULT])
            self.setBrush(self.default_brush)

        super().paint(painter, option, widget)

        # Draw corner handles
        rect = self.rect()
        handle_brush = QBrush(self.color)
        handle_pen = QPen(self.color)

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

    def set_selected(self, selected: bool) -> None:
        self.setSelected(selected)
        self.update()

    def set_movable(self, movable: bool) -> None:
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.update()

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self.box_moved.emit(self.box_id, value.x(), value.y())
        # elif change == QGraphicsItem.GraphicsItemChange.ItemTransformChange:
        #     rect = self.rect()
        #     self.box_resized.emit(
        #         self.box_id, rect.x(), rect.y(), rect.width(), rect.height()
        #     )
        return super().itemChange(change, value)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
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

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
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

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
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
            self.box_resized.emit(
                self.box_id, rect.x(), rect.y(), rect.width(), rect.height()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.resizing = False
        self.set_movable(False)
        super().mouseReleaseEvent(event)
