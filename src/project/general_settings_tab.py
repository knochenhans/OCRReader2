from PySide6.QtGui import QColor, QPalette, Qt

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QColorDialog,
)

from settings import Settings  # type: ignore


class GeneralSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Thumbnail Size Layout
        thumbnail_layout = QHBoxLayout()
        self.thumbnail_size_label = QLabel("Thumbnail Size:", self)
        self.thumbnail_size_edit = QLineEdit(self)
        self.thumbnail_size_edit.textChanged.connect(self.update_thumbnail_size)

        thumbnail_layout.addWidget(self.thumbnail_size_label)
        thumbnail_layout.addWidget(self.thumbnail_size_edit)

        main_layout.addLayout(thumbnail_layout)

        # OCR Editor Group
        ocr_editor_group = QVBoxLayout()
        ocr_editor_group.setAlignment(Qt.AlignmentFlag.AlignTop)
        ocr_editor_label = QLabel("OCR Editor", self)
        ocr_editor_group.addWidget(ocr_editor_label)

        # Merged Word in Dictionary Layout
        in_dict_layout = QHBoxLayout()
        self.merged_word_in_dict_label = QLabel("Merged Word in Dictionary:", self)
        self.merged_word_in_dict_button = QPushButton(self)
        self.merged_word_in_dict_button.setFixedWidth(50)
        self.merged_word_in_dict_button.clicked.connect(self.choose_color_in_dict)

        in_dict_layout.addWidget(self.merged_word_in_dict_label)
        in_dict_layout.addWidget(self.merged_word_in_dict_button)

        ocr_editor_group.addLayout(in_dict_layout)

        # Merged Word not in Dictionary Layout
        not_in_dict_layout = QHBoxLayout()
        self.merged_word_not_in_dict_label = QLabel(
            "Merged Word not in Dictionary:", self
        )
        self.merged_word_not_in_dict_button = QPushButton(self)
        self.merged_word_not_in_dict_button.setFixedWidth(50)
        self.merged_word_not_in_dict_button.clicked.connect(
            self.choose_color_not_in_dict
        )

        not_in_dict_layout.addWidget(self.merged_word_not_in_dict_label)
        not_in_dict_layout.addWidget(self.merged_word_not_in_dict_button)

        ocr_editor_group.addLayout(not_in_dict_layout)

        main_layout.addLayout(ocr_editor_group)

        self.setLayout(main_layout)

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
        self.thumbnail_size_edit.setText(
            str(self.application_settings.get("thumbnail_size", 150))
        )

        # Set default colors if not available in settings
        default_color_in_dict = self.application_settings.get(
            "merged_word_in_dict_color", QColor(0, 255, 0, 255).rgba()
        )
        default_color_not_in_dict = self.application_settings.get(
            "merged_word_not_in_dict_color", QColor(255, 0, 0, 255).rgba()
        )

        self.set_button_color(self.merged_word_in_dict_button, default_color_in_dict)
        self.set_button_color(
            self.merged_word_not_in_dict_button, default_color_not_in_dict
        )

    def update_thumbnail_size(self) -> None:
        thumbnail_size = int(self.thumbnail_size_edit.text())
        self.application_settings.set("thumbnail_size", thumbnail_size)

    def choose_color_in_dict(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            rgba = color.rgba()
            self.application_settings.set("merged_word_in_dict_color", rgba)
            self.set_button_color(self.merged_word_in_dict_button, rgba)

    def choose_color_not_in_dict(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            rgba = color.rgba()
            self.application_settings.set("merged_word_not_in_dict_color", rgba)
            self.set_button_color(self.merged_word_not_in_dict_button, rgba)

    def set_button_color(self, button: QPushButton, color: int) -> None:
        qcolor = QColor.fromRgb(color)
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Button, qcolor)
        button.setPalette(palette)
        button.setAutoFillBackground(True)
