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
from loguru import logger


class BoxItemSelectionState(Enum):
    DEFAULT = 1
    SELECTED = 2


class BoxItemState(Enum):
    IDLE = 1
    MOVING = 2
    RESIZING = 3


class ResizeCorner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class BoxItem(QGraphicsRectItem, QObject):
    box_moved = Signal(str, QPointF)
    box_resized = Signal(str, QPointF, QPointF)
    box_right_clicked = Signal(str)

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
        self.state = BoxItemState.IDLE
        self.resize_margin = 20
        self.handle_size = 6
        self.is_recognized = False

        self.set_movable(True)

    def update_pens_and_brushes(self) -> None:
        self.border_pens = {
            BoxItemSelectionState.DEFAULT: QPen(self.color, 1, Qt.PenStyle.SolidLine),
            BoxItemSelectionState.SELECTED: QPen(self.color, 2, Qt.PenStyle.DashLine),
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
            self.setPen(self.border_pens[BoxItemSelectionState.SELECTED])
            self.setBrush(self.selected_brush)
        else:
            self.setPen(self.border_pens[BoxItemSelectionState.DEFAULT])
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

        # Draw ✓ if recognized
        if self.is_recognized:
            painter.setPen(QPen(Qt.GlobalColor.green))
            if widget is not None:
                font = widget.font()
                font.setPointSize(font.pointSize() + 4)  # Increase font size
                painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, "✓")

    def set_selected(self, selected: bool) -> None:
        self.setSelected(selected)
        self.update()

    def set_movable(self, movable: bool) -> None:
        # logger.debug(f"Enabling box movement: {movable}")
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.update()

    def set_selectable(self, selectable: bool) -> None:
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, selectable)
        self.update()

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if isinstance(value, QPointF):
                self.box_moved.emit(self.box_id, value)
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
        if event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click()
        elif self.is_in_resize_margin(pos, rect.topLeft()):
            self.start_resizing(ResizeCorner.TOP_LEFT)
        elif self.is_in_resize_margin(pos, rect.topRight()):
            self.start_resizing(ResizeCorner.TOP_RIGHT)
        elif self.is_in_resize_margin(pos, rect.bottomLeft()):
            self.start_resizing(ResizeCorner.BOTTOM_LEFT)
        elif self.is_in_resize_margin(pos, rect.bottomRight()):
            self.start_resizing(ResizeCorner.BOTTOM_RIGHT)
        else:
            # Check movable flag
            if self.flags() & QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable:
                self.start_moving()
        super().mousePressEvent(event)

    def handle_right_click(self) -> None:
        logger.debug(f"Box item {self.box_id} right clicked")
        self.box_right_clicked.emit(self.box_id)

    def is_in_resize_margin(self, pos: QPointF, corner: QPointF) -> bool:
        return (
            corner.x() - self.resize_margin
            <= pos.x()
            <= corner.x() + self.resize_margin
            and corner.y() - self.resize_margin
            <= pos.y()
            <= corner.y() + self.resize_margin
        )

    def start_resizing(self, corner: ResizeCorner) -> None:
        self.state = BoxItemState.RESIZING
        self.resize_corner = corner
        self.set_movable(False)

    def start_moving(self) -> None:
        self.state = BoxItemState.MOVING
        self.set_movable(True)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.state == BoxItemState.RESIZING:
            self.prepareGeometryChange()
            pos = event.pos()
            rect = self.rect()
            if self.resize_corner == ResizeCorner.TOP_LEFT:
                logger.debug(f"Resizing left: {pos.x()}, top: {pos.y()}")
                rect.setTopLeft(pos)
            elif self.resize_corner == ResizeCorner.TOP_RIGHT:
                logger.debug(f"Resizing right: {pos.x()}, top: {pos.y()}")
                rect.setTopRight(pos)
            elif self.resize_corner == ResizeCorner.BOTTOM_LEFT:
                logger.debug(f"Resizing left: {pos.x()}, bottom: {pos.y()}")
                rect.setBottomLeft(pos)
            elif self.resize_corner == ResizeCorner.BOTTOM_RIGHT:
                logger.debug(f"Resizing right: {pos.x()}, bottom: {pos.y()}")
                rect.setBottomRight(pos)
            self.setRect(rect)
            self.box_resized.emit(
                self.box_id, rect.topLeft(), rect.bottomRight() - rect.topLeft()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.state = BoxItemState.IDLE
        # self.set_movable(False)
        super().mouseReleaseEvent(event)
