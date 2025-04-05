from dataclasses import dataclass
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
    QCheckBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QStyle,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont
from typing import Tuple, Callable
from enum import auto

from settings.settings import Settings  # type: ignore


class SettingType(Enum):
    EDIT_TEXT = auto()
    CHECKBOX = auto()
    COMBOBOX = auto()
    SPINBOX_INT = auto()
    SPINBOX_FLOAT = auto()
    COLOR = auto()
    FONT = auto()
    TABLE = auto()
    FOLDER = auto()


@dataclass
class SettingLayout:
    category: str
    key: str
    setting_type: SettingType
    label: str
    action: Callable[[], None]
    data_type: Optional[type] = None  # Data type (e.g., int, float)
    bottom: Optional[float] = None  # Minimum value for numeric settings
    top: Optional[float] = None  # Maximum value for numeric settings
    decimals: Optional[int] = (
        None  # Number of decimals for float settings (if applicable)
    )


class SettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.settings: Settings = Settings()
        self.setting_elements: Dict[str, QWidget] = {}
        self.settings_layouts: Tuple

    def create_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout_groups: Dict[str, QVBoxLayout] = {}

        for setting in self.settings_layouts:
            group_name = setting.category
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

            if setting.setting_type == SettingType.EDIT_TEXT:
                group_layout.addLayout(self.create_label_edit_layout(setting))
            elif setting.setting_type == SettingType.COLOR:
                group_layout.addLayout(self.create_color_layout(setting))
            elif setting.setting_type == SettingType.FONT:
                group_layout.addLayout(self.create_font_chooser_layout(setting))
            elif setting.setting_type == SettingType.CHECKBOX:
                group_layout.addLayout(self.create_checkbox_layout(setting))
            elif setting.setting_type == SettingType.COMBOBOX:
                group_layout.addLayout(self.create_combobox_layout(setting))
            elif setting.setting_type == SettingType.SPINBOX_INT:
                group_layout.addLayout(self.create_spinbox_int_layout(setting))
            elif setting.setting_type == SettingType.SPINBOX_FLOAT:
                group_layout.addLayout(self.create_spinbox_float_layout(setting))
            elif setting.setting_type == SettingType.FOLDER:
                group_layout.addLayout(self.create_folder_layout(setting))

        self.setLayout(main_layout)

    def create_color_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        button = self.create_color_button(setting.action)

        layout.addWidget(label)
        layout.addWidget(button)

        self.setting_elements[setting.key] = button

        return layout

    def create_font_chooser_layout(self, setting: SettingLayout) -> QHBoxLayout:
        font_chooser_layout = QHBoxLayout()
        font_label = QLabel(setting.label, self)
        font_button = QPushButton(setting.label, self)
        font_button.clicked.connect(setting.action)

        font_chooser_layout.addWidget(font_label)
        font_chooser_layout.addWidget(font_button)

        self.setting_elements[setting.key] = font_button

        return font_chooser_layout

    def create_label_edit_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        edit = QLineEdit(self)

        edit.textChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(edit)

        self.setting_elements[setting.key] = edit

        return layout

    def create_checkbox_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        checkbox = QCheckBox(self)
        checkbox.stateChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(checkbox)

        self.setting_elements[setting.key] = checkbox

        return layout

    def create_combobox_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        combobox = QComboBox(self)
        combobox.currentIndexChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(combobox)

        self.setting_elements[setting.key] = combobox

        return layout

    def create_spinbox_int_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        spinbox = QSpinBox(self)

        # Set range using bottom and top values
        if setting.bottom is not None and setting.top is not None:
            spinbox.setRange(int(setting.bottom), int(setting.top))

        spinbox.valueChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(spinbox)

        self.setting_elements[setting.key] = spinbox

        return layout

    def create_spinbox_float_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        spinbox = QDoubleSpinBox(self)

        # Set range and decimals using bottom, top, and decimals values
        if setting.bottom is not None and setting.top is not None:
            spinbox.setRange(setting.bottom, setting.top)
        if setting.decimals is not None:
            spinbox.setDecimals(setting.decimals)

        spinbox.valueChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(spinbox)

        self.setting_elements[setting.key] = spinbox

        return layout

    def set_button_color(self, button: QPushButton, color: int) -> None:
        qcolor = QColor.fromRgb(color)
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Button, qcolor)
        button.setPalette(palette)
        button.setAutoFillBackground(True)

    def create_color_button(self, slot: Callable[[], None]) -> QPushButton:
        button = QPushButton(self)
        button.setFixedWidth(50)
        button.clicked.connect(slot)
        return button

    def load_line_edit_setting(self, key: str, default_value: str) -> None:
        line_edit = self.setting_elements.get(key)
        if isinstance(line_edit, QLineEdit):
            value = self.settings.get(key, default_value)
            line_edit.setText(str(value))

    def load_folder_setting(self, key: str, default_value: str) -> None:
        self.load_line_edit_setting(key, default_value)

    def load_color_setting(self, key: str, default_value: int) -> None:
        button = self.setting_elements.get(key)
        if isinstance(button, QPushButton):
            color = self.settings.get(key, default_value)
            self.set_button_color(button, color)

    def load_font_setting(self, key: str, default_font: QFont) -> None:
        button = self.setting_elements.get(key)
        if isinstance(button, QPushButton):
            font = self.settings.get(key, default_font)
            button.setText(f"{font.family()}, {font.pointSize()}")
            button.setFont(font)

    def choose_color(self, setting_key: str) -> None:
        button = self.setting_elements.get(setting_key)
        if self.settings and isinstance(button, QPushButton):
            color = QColorDialog.getColor()
            if color.isValid():
                rgba = color.rgba()
                self.settings.set(setting_key, rgba)
                self.set_button_color(button, rgba)

    def choose_font(self, setting_key: str) -> None:
        button = self.setting_elements.get(setting_key)
        if self.settings and isinstance(button, QPushButton):
            current_font = self.settings.get(setting_key, QFont())
            ok, font = QFontDialog.getFont(current_font, self)
            if ok:
                self.settings.set(setting_key, font)
                button.setText(f"{font.family()}, {font.pointSize()}")
                button.setFont(font)

    def load_settings(self, application_settings: Settings) -> None:
        pass

    def create_vertical_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return layout

    def load_spinbox_int_setting(self, key: str, default_value: int) -> None:
        spinbox = self.setting_elements.get(key)
        if isinstance(spinbox, QSpinBox):
            value = self.settings.get(key, default_value)
            spinbox.setValue(value)

    def load_spinbox_float_setting(self, key: str, default_value: float) -> None:
        spinbox = self.setting_elements.get(key)
        if isinstance(spinbox, QDoubleSpinBox):
            value = self.settings.get(key, default_value)
            spinbox.setValue(value)

    def load_combobox_setting(self, key: str, default_value: str) -> None:
        combobox = self.setting_elements.get(key)
        if isinstance(combobox, QComboBox):
            value = self.settings.get(key, default_value)
            index = combobox.findText(value)
            if index != -1:
                combobox.setCurrentIndex(index)

    def load_checkbox_setting(self, key: str, default_value: bool) -> None:
        checkbox = self.setting_elements.get(key)
        if isinstance(checkbox, QCheckBox):
            value = self.settings.get(key, default_value)
            checkbox.setChecked(value)

    def update_checkbox_setting(self, key: str) -> None:
        checkbox = self.setting_elements.get(key)
        if self.settings and isinstance(checkbox, QCheckBox):
            value = checkbox.isChecked()
            self.settings.set(key, value)

    def update_combobox_setting(self, key: str) -> None:
        combobox = self.setting_elements.get(key)
        if self.settings and isinstance(combobox, QComboBox):
            value = combobox.currentText()
            self.settings.set(key, value)

    def update_spinbox_int_setting(self, key: str) -> None:
        spinbox = self.setting_elements.get(key)
        if self.settings and isinstance(spinbox, QSpinBox):
            value = spinbox.value()
            self.settings.set(key, value)

    def update_spinbox_float_setting(self, key: str) -> None:
        spinbox = self.setting_elements.get(key)
        if self.settings and isinstance(spinbox, QDoubleSpinBox):
            value = spinbox.value()
            self.settings.set(key, value)

    def update_line_edit_setting(self, key: str) -> None:
        line_edit = self.setting_elements.get(key)
        if self.settings and isinstance(line_edit, QLineEdit):
            value = line_edit.text()
            self.settings.set(key, value)

    def update_color_setting(self, key: str) -> None:
        button = self.setting_elements.get(key)
        if self.settings and isinstance(button, QPushButton):
            color = button.palette().color(QPalette.ColorRole.Button).rgba()
            self.settings.set(key, color)

    def update_font_setting(self, key: str) -> None:
        button = self.setting_elements.get(key)
        if self.settings and isinstance(button, QPushButton):
            font = button.font()
            self.settings.set(key, font)

    def fill_combo_box(self, key: str, items: list[str]) -> None:
        combobox = self.setting_elements.get(key)
        if isinstance(combobox, QComboBox):
            # Temporarily disconnect the signal to avoid triggering update_combobox_setting
            try:
                combobox.currentIndexChanged.disconnect()
            except TypeError:
                # Signal was not connected, so no need to disconnect
                pass

            # Populate the QComboBox
            combobox.clear()
            for value in items:
                combobox.addItem(value)

            # Reconnect the signal
            combobox.currentIndexChanged.connect(
                lambda: self.update_combobox_setting(key)
            )

    def create_folder_layout(self, setting: SettingLayout) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(setting.label, self)
        folder_edit = QLineEdit(self)
        folder_button = QPushButton(self)
        folder_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        )

        # Connect the button to open a folder dialog
        folder_button.clicked.connect(
            lambda: self.choose_folder(setting.key, folder_edit)
        )

        # Connect the QLineEdit to update the setting when text changes
        folder_edit.textChanged.connect(setting.action)

        layout.addWidget(label)
        layout.addWidget(folder_edit)
        layout.addWidget(folder_button)

        # Store the QLineEdit in the setting elements for later access
        self.setting_elements[setting.key] = folder_edit

        return layout

    def choose_folder(self, key: str, folder_edit: QLineEdit) -> None:
        from PySide6.QtWidgets import QFileDialog

        # Use the current text in the QLineEdit as the start path
        start_path = folder_edit.text() if folder_edit.text() else "/"
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", start_path)
        if folder:
            folder_edit.setText(folder)  # Update the QLineEdit with the selected folder
            if self.settings:
                self.settings.set(key, folder)  # Save the folder path to the settings
