from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit

from settings import Settings  # type: ignore


class GeneralSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()

        layout = QHBoxLayout(self)

        self.tesseract_options_label = QLabel("Tesseract Options:", self)
        self.tesseract_options_edit = QLineEdit(self)
        self.tesseract_options_edit.textChanged.connect(self.update_tesseract_options)

        layout.addWidget(self.tesseract_options_label)
        layout.addWidget(self.tesseract_options_edit)

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
        self.tesseract_options_edit.setText(
            self.application_settings.get("tesseract_options", "")
        )

    def update_tesseract_options(self) -> None:
        self.application_settings.set(
            "tesseract_options", self.tesseract_options_edit.text()
        )
