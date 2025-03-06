from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit

from settings import Settings  # type: ignore


class GeneralSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()

        layout = QHBoxLayout(self)

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
