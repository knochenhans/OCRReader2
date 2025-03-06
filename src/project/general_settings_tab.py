from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class GeneralSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
