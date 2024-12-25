from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

from .line_break_controller import LineBreakController
from page.ocr_box import TextBox # type: ignore
from page.box_type import BoxType # type: ignore


class LineBreakDialog(QDialog):
    def __init__(self):
        super().__init__()

        text_box = TextBox(0, 0, 0, 0, BoxType.FLOWING_TEXT)
        text_box.user_text = """Drei erstklassige Rennpfer-
        de hat Commodore mit den Amigas im Stall. Der Amiga 500 wird für frischen Wind in der gehobenen Heimcompu-
        terszene sorgen. Mit eingebau-
        tem."""

        self.controller = LineBreakController(text_box, "de")

        self.setWindowTitle("Simple Dialog")

        self.main_layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.main_layout.addWidget(self.text_edit)

        self.button = QPushButton("Close", self)
        self.button.clicked.connect(self.close)
        self.main_layout.addWidget(self.button)

        self.setLayout(self.main_layout)
