from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

from settings.settings import Settings  # type: ignore
from settings.settings_tab import SettingsTab, SettingType, SettingLayout  # type: ignore
from page.box_type import BoxType  # type: ignore


class ExportSettingsTab(SettingsTab):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.box_type_table: Optional[QTableWidget] = None

        self.settings_layouts: List[SettingLayout] = [
            SettingLayout(
                category="Export Settings",
                key="max_font_size",
                setting_type=SettingType.SPINBOX_INT,
                label="Max. Font Size:",
                action=lambda: self.update_spinbox_int_setting("max_font_size"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="Export Settings",
                key="min_font_size",
                setting_type=SettingType.SPINBOX_INT,
                label="Min. Font Size:",
                action=lambda: self.update_spinbox_int_setting("min_font_size"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="Export Settings",
                key="round_font_size",
                setting_type=SettingType.SPINBOX_FLOAT,
                label="Round Font Size by:",
                action=lambda: self.update_spinbox_float_setting("round_font_size"),
                data_type=float,
                bottom=0.0,
                top=10.0,
                decimals=2,
            ),
            SettingLayout(
                category="Export Settings",
                key="scale_factor",
                setting_type=SettingType.SPINBOX_FLOAT,
                label="Scale Factor:",
                action=lambda: self.update_spinbox_float_setting("scale_factor"),
                data_type=float,
                bottom=0.0,
                top=10.0,
                decimals=2,
            ),
            SettingLayout(
                category="Export Settings",
                key="box_type_tags",
                setting_type=SettingType.TABLE,
                label="Box Type Tags:",
                action=lambda: self.update_box_type_tags(),
            ),
        ]

        self.create_layout()

    def create_table_layout(self, setting: SettingLayout) -> QWidget:
        """Create a table layout for box type tags."""
        self.box_type_table = QTableWidget(len(BoxType), 2)
        self.box_type_table.setHorizontalHeaderLabels(["Box Type", "Custom Tag"])
        self.box_type_table.horizontalHeader().setStretchLastSection(True)

        for row, box_type in enumerate(BoxType):
            box_type_item = QTableWidgetItem(box_type.name)
            box_type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.box_type_table.setItem(row, 0, box_type_item)
            custom_tag_item = QTableWidgetItem()
            self.box_type_table.setItem(row, 1, custom_tag_item)

        layout = QWidget()
        layout_layout = self.create_vertical_layout()
        layout_layout.addWidget(QLabel(setting.label))
        layout_layout.addWidget(self.box_type_table)
        layout.setLayout(layout_layout)

        return layout

    def load_settings(self, application_settings: Settings) -> None:
        """Load settings into the UI."""
        self.settings = application_settings

        self.load_spinbox_int_setting("max_font_size", 0)
        self.load_spinbox_int_setting("min_font_size", 0)

        self.load_spinbox_float_setting("round_font_size", 0.0)
        self.load_spinbox_float_setting("scale_factor", 1.0)

        self.load_table_setting("box_type_tags")

    def load_table_setting(self, key: str) -> None:
        """Load data into the table for box type tags."""
        if self.box_type_table:
            box_type_tags = self.settings.get(key, {})
            for row, box_type in enumerate(BoxType):
                custom_tag = box_type_tags.get(box_type.name, "")
                self.box_type_table.item(row, 1).setText(custom_tag)

    def update_box_type_tags(self) -> None:
        """Update box type tags in the settings."""
        if self.settings and self.box_type_table:
            tags = {}
            for row, box_type in enumerate(BoxType):
                custom_tag = self.box_type_table.item(row, 1).text()
                tags[box_type.name] = custom_tag
            self.settings.set("box_type_tags", tags)
