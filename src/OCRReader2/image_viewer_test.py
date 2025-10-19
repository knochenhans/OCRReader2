import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ocr_edit_dialog.image_viewer import ImageViewer


class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Viewer Example")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the ImageViewer instance
        self.image_viewer = ImageViewer(self)
        layout.addWidget(self.image_viewer)

        self.add_boxes_button = QPushButton("Add Boxes")
        self.add_boxes_button.clicked.connect(self.add_boxes)
        layout.addWidget(self.add_boxes_button)

        # Always load the specified image on startup
        self.load_default_image()

    def load_default_image(self):
        # Load the default image
        file_path = "/tmp/Bildschirmfoto_2025-04-12_00-29-01.png"
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.image_viewer.add_pixmaps([pixmap, pixmap])
            # self.image_viewer.updateGeometry()
            # self.image_viewer.update()

    def add_boxes(self):
        # Define some example boxes with colors
        boxes = [
            ((50, 50, 100, 100), QColor(Qt.GlobalColor.red)),
            ((200, 150, 120, 80), QColor(Qt.GlobalColor.green)),
            ((400, 300, 150, 150), QColor(Qt.GlobalColor.blue)),
        ]
        self.image_viewer.add_boxes(boxes, 0)
        self.image_viewer.add_boxes(boxes, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer_app = ImageViewerApp()
    viewer_app.show()
    sys.exit(app.exec())
