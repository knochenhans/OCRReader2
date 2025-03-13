from enum import Enum, auto
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
from PySide6.QtCore import QPointF, QRectF, QSizeF, Signal, QObject

from settings import Settings  # type: ignore


class BoxItemSelectionState(Enum):
    DEFAULT = auto()
    SELECTED = auto()


class BoxItemState(Enum):
    IDLE = auto()
    MOVING = auto()
    RESIZING = auto()
    DISABLED = auto()


class ResizeCorner(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class BoxItem(QGraphicsRectItem, QObject):
    box_moved = Signal(str, QPointF)
    box_resized = Signal(str, QPointF, QPointF)
    box_started_resizing = Signal(str)
    box_started_moving = Signal(str)

    def __init__(
        self,
        id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        parent: Optional[QGraphicsItem] = None,
        application_settings: Optional[Settings] = None,
    ) -> None:
        QGraphicsRectItem.__init__(self, x, y, width, height, parent)
        QObject.__init__(self)

        self.application_settings = application_settings

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
        self.has_user_text = False
        self.has_user_data = False
        self.flows_into_next = False
        self.order = 0

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

        border_offset = 15

        if not self.application_settings:
            return

        box_item_symbol_font_size = self.application_settings.get(
            "box_item_symbol_size", 16
        )
        box_item_symbol_font = painter.font()
        box_item_symbol_font.setPointSize(box_item_symbol_font_size)
        painter.setFont(box_item_symbol_font)

        box_item_symbol_font_color = self.application_settings.get(
            "box_item_symbol_font_color", Qt.GlobalColor.green
        )
        painter.setPen(QPen(box_item_symbol_font_color))

        def draw_symbol(
            condition: bool,
            rect: QRectF,
            alignment: Qt.AlignmentFlag,
            symbol_key: str,
            default_symbol: str,
        ) -> None:
            if condition and self.application_settings is not None:
                painter.drawText(
                    rect,
                    alignment,
                    self.application_settings.get(symbol_key, default_symbol),
                )

        # Draw ✓ if recognized
        draw_symbol(
            self.is_recognized,
            rect.adjusted(0, 0, border_offset, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
            "box_item_is_recognized_symbol",
            "✓",
        )

        # Draw ✎ if user text
        draw_symbol(
            self.has_user_text,
            rect.adjusted(-border_offset, -border_offset, 0, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            "box_item_has_user_text_symbol",
            "✎",
        )

        # Draw → if flows into next
        draw_symbol(
            self.flows_into_next,
            rect.adjusted(0, 0, border_offset, border_offset),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
            "box_item_flows_into_next_symbol",
            "→",
        )

        # Draw ⚙ if has user data
        draw_symbol(
            self.has_user_data,
            rect.adjusted(0, 0, border_offset, border_offset),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
            "box_item_has_user_data_symbol",
            "⚙",
        )

        # Draw order number
        painter.setPen(
            QPen(
                self.application_settings.get(
                    "box_item_order_font_color", Qt.GlobalColor.blue
                )
            )
        )
        painter.drawText(
            rect.adjusted(-border_offset, 0, 0, 0),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            str(self.order),
        )

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
        if self.state != BoxItemState.IDLE:
            return

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

        if self.is_in_resize_margin(pos, rect.topLeft()):
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

    def enable(self, enable: bool) -> None:
        if enable:
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
            self.state = BoxItemState.IDLE
        else:
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, False)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, False)
            self.state = BoxItemState.DISABLED

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.state == BoxItemState.RESIZING:
            self.prepareGeometryChange()
            pos = event.pos()
            rect = self.rect()
            min_size = self.handle_size * 2  # Minimum size to prevent inversion

            if self.resize_corner == ResizeCorner.TOP_LEFT:
                new_width = rect.right() - pos.x()
                new_height = rect.bottom() - pos.y()
                if new_width >= min_size and new_height >= min_size:
                    rect.setTopLeft(pos)
            elif self.resize_corner == ResizeCorner.TOP_RIGHT:
                new_width = pos.x() - rect.left()
                new_height = rect.bottom() - pos.y()
                if new_width >= min_size and new_height >= min_size:
                    rect.setTopRight(pos)
            elif self.resize_corner == ResizeCorner.BOTTOM_LEFT:
                new_width = rect.right() - pos.x()
                new_height = pos.y() - rect.top()
                if new_width >= min_size and new_height >= min_size:
                    rect.setBottomLeft(pos)
            elif self.resize_corner == ResizeCorner.BOTTOM_RIGHT:
                new_width = pos.x() - rect.left()
                new_height = pos.y() - rect.top()
                if new_width >= min_size and new_height >= min_size:
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
