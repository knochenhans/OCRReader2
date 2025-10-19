from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsItem,
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QBrush, QColor, QPainter, QFont


class MovableBox(QGraphicsRectItem):
    def __init__(self, rect, order_number):
        super().__init__(rect)
        self.setBrush(QBrush(QColor(100, 100, 250)))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.order_number = order_number

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        # Save the current painter state
        painter.save()

        # Reset the transformation for the text
        painter.resetTransform()

        # Calculate the position of the text
        text_position = self.mapToScene(self.rect().topLeft() + QPointF(5, 15))

        # Set the font and pen for the text
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor(0, 0, 0))

        # Draw the text at the calculated position
        painter.drawText(text_position, str(self.order_number))

        # Restore the painter state
        painter.restore()


class SceneViewApp(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene_obj = QGraphicsScene()
        self.setScene(self.scene_obj)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Movable Box Scene")
        self.setGeometry(100, 100, 800, 600)

        self.box = MovableBox(QRectF(0, 0, 100, 100), order_number=1)
        self.scene_obj.addItem(self.box)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)


if __name__ == "__main__":
    app = QApplication([])
    view = SceneViewApp()
    view.show()
    app.exec()
