from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout

from settings import Settings  # type: ignore


class GeneralSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()

        main_layout = QVBoxLayout(self)

        thumbnail_layout = QHBoxLayout()
        self.thumbnail_size_label = QLabel("Thumbnail Size:", self)
        self.thumbnail_size_edit = QLineEdit(self)
        self.thumbnail_size_edit.textChanged.connect(self.update_thumbnail_size)

        thumbnail_layout.addWidget(self.thumbnail_size_label)
        thumbnail_layout.addWidget(self.thumbnail_size_edit)

        main_layout.addLayout(thumbnail_layout)

        self.setLayout(main_layout)

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
        self.thumbnail_size_edit.setText(
            str(self.application_settings.get("thumbnail_size", 150))
        )

    def update_thumbnail_size(self) -> None:
        thumbnail_size = int(self.thumbnail_size_edit.text())
        self.application_settings.set("thumbnail_size", thumbnail_size)
