from enum import Enum, auto
from PySide6.QtCore import Qt, QRectF, QSizeF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QGraphicsLineItem,
    QGraphicsItem,
)


class HEADER_FOOTER_ITEM_TYPE(Enum):
    HEADER = auto()
    FOOTER = auto()


class HeaderFooterItem(QGraphicsRectItem):
    def __init__(self, type: HEADER_FOOTER_ITEM_TYPE, page_size: QSizeF, y: float):
        super().__init__()

        rect = QRectF()

        rect.setX(0)
        rect.setWidth(page_size.width())

        if type is HEADER_FOOTER_ITEM_TYPE.HEADER:
            title = "Header"
            rect.setBottom(y)
        else:
            title = "Footer"
            rect.setTop(y)
            rect.setBottom(page_size.height())

        self.setRect(rect)

        brush = QBrush(QColor(128, 0, 200, 150))
        brush.setStyle(Qt.BrushStyle.BDiagPattern)

        self.setPen(Qt.PenStyle.NoPen)
        self.setBrush(brush)

        pen = QPen(QColor(128, 0, 200, 150))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setCosmetic(True)

        self.title = QGraphicsSimpleTextItem(self)
        self.title.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.title.setPen(pen)
        self.title.setText(title)

        self.line = QGraphicsLineItem(self)
        self.line.setPen(QPen(QColor(128, 0, 200, 200), 3, Qt.PenStyle.SolidLine))
        self.line.setPos(0, y)
        self.line.setLine(0, 0, self.rect().width(), 0)

        self.setZValue(10)

    def update_title(self):
        self.title.setPos(5, self.rect().y() + 5)

    def update_bottom_position(self, y: float):
        rect = self.rect()
        rect.setBottom(y)
        self.setRect(rect)
        self.line.setPos(0, y)

    def update_top_position(self, y: float):
        rect = self.rect()
        rect.setTop(y)
        self.setRect(rect)
        self.line.setPos(0, y)
        self.title.setPos(5, self.rect().y() + 5)
