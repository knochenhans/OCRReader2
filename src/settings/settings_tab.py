from enum import Enum
from typing import Dict, Optional

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QColorDialog,
    QFontDialog,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QColor, QPalette, QFont
from typing import Tuple, Callable

from settings.settings import Settings  # type: ignore


class SettingType(Enum):
    EDIT = 1
    COLOR = 2
    FONT = 3


class SettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()
        self.setting_elements: Dict[str, QWidget] = {}
        self.settings_layouts: Tuple

    def create_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout_groups: Dict[str, QVBoxLayout] = {}

        for setting in self.settings_layouts:
            group_name = setting[0]
            if group_name not in layout_groups:
                group_layout = QVBoxLayout()
                group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                layout_groups[group_name] = group_layout

                group_label = QLabel(group_name)
                font = group_label.font()
                font.setBold(True)
                font.setPointSize(12)
                group_label.setFont(font)
                main_layout.addWidget(group_label)
                main_layout.addLayout(group_layout)
            else:
                group_layout = layout_groups[group_name]

            element_setting = setting[1:]

            if element_setting[1] == SettingType.EDIT:
                group_layout.addLayout(self.create_label_edit_layout(element_setting))
            elif element_setting[1] == SettingType.COLOR:
                group_layout.addLayout(self.create_color_layout(element_setting))
            elif element_setting[1] == SettingType.FONT:
                group_layout.addLayout(self.create_font_chooser_layout(element_setting))

        self.setLayout(main_layout)

    def create_color_layout(
        self,
        color_info: Tuple[str, SettingType, str, Callable, Optional[QIntValidator]],
    ) -> QHBoxLayout:
        key, _, label_text, slot, _ = color_info
        layout = QHBoxLayout()
        label = QLabel(label_text, self)
        button = self.create_color_button(slot)

        layout.addWidget(label)
        layout.addWidget(button)

        self.setting_elements[key] = button

        return layout

    def create_font_chooser_layout(
        self,
        layout_info: Tuple[str, SettingType, str, Callable, Optional[QIntValidator]],
    ) -> QHBoxLayout:
        key, _, label_text, slot, _ = layout_info
        font_chooser_layout = QHBoxLayout()
        self.font_size_label = QLabel(label_text, self)
        self.font_size_button = QPushButton(label_text, self)
        self.font_size_button.clicked.connect(slot)

        font_chooser_layout.addWidget(self.font_size_label)
        font_chooser_layout.addWidget(self.font_size_button)

        self.setting_elements[key] = self.font_size_button

        return font_chooser_layout

    def create_label_edit_layout(
        self,
        layout_info: Tuple[str, SettingType, str, Callable, Optional[QIntValidator]],
    ) -> QHBoxLayout:
        key, _, label_text, slot, validator = layout_info
        layout = QHBoxLayout()
        label = QLabel(label_text, self)
        edit = QLineEdit(self)
        if validator:
            edit.setValidator(validator)
        edit.textChanged.connect(slot)

        layout.addWidget(label)
        layout.addWidget(edit)

        self.setting_elements[key] = edit

        return layout

    def set_button_color(self, button: QPushButton, color: int) -> None:
        qcolor = QColor.fromRgb(color)
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Button, qcolor)
        button.setPalette(palette)
        button.setAutoFillBackground(True)

    def create_color_button(self, slot) -> QPushButton:
        button = QPushButton(self)
        button.setFixedWidth(50)
        button.clicked.connect(slot)
        return button

    def load_line_edit_setting(self, key: str, default_value: int) -> None:
        line_edit = self.setting_elements.get(key)
        if isinstance(line_edit, QLineEdit):
            line_edit.setText(str(self.application_settings.get(key, default_value)))

    def load_color_setting(self, key: str, default_value: int) -> None:
        button = self.setting_elements.get(key)
        if isinstance(button, QPushButton):
            color = self.application_settings.get(key, default_value)
            self.set_button_color(button, color)

    def load_font_setting(self, key: str, default_font: QFont) -> None:
        button = self.setting_elements.get(key)
        if isinstance(button, QPushButton):
            font = self.application_settings.get(key, default_font)
            button.setText(f"{font.family()}, {font.pointSize()}")
            button.setFont(font)

    def update_line_edit_setting(self, key: str) -> None:
        line_edit = self.setting_elements.get(key)
        if self.application_settings and isinstance(line_edit, QLineEdit):
            value = int(line_edit.text())
            self.application_settings.set(key, value)

    def choose_color(self, setting_key: str) -> None:
        button = self.setting_elements.get(setting_key)
        if self.application_settings and isinstance(button, QPushButton):
            color = QColorDialog.getColor()
            if color.isValid():
                rgba = color.rgba()
                self.application_settings.set(setting_key, rgba)
                self.set_button_color(button, rgba)

    def choose_font(self, setting_key: str) -> None:
        button = self.setting_elements.get(setting_key)
        if self.application_settings and isinstance(button, QPushButton):
            current_font = self.application_settings.get(setting_key, QFont())
            ok, font = QFontDialog.getFont(current_font, self)
            if ok:
                self.application_settings.set(setting_key, font)
                button.setText(f"{font.family()}, {font.pointSize()}")
                button.setFont(font)

    def load_settings(self, application_settings: Settings) -> None:
        pass
