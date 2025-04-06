from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit


class CustomTextEditor(QLineEdit):
    ctrl_enter_pressed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText("Enter text here...")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("font-size: 20px; font-family: 'Courier New', monospace;")

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.ctrl_enter_pressed.emit()
        else:
            super().keyPressEvent(event)
