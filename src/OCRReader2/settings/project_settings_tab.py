from typing import List, Optional

from iso639 import Lang
from papersize import SIZES  # type: ignore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLayout, QListWidget, QListWidgetItem, QWidget
from SettingsManager import SettingsManager

from OCRReader2.ocr_engine.analyzer_registry import ANALYZER_REGISTRY
from OCRReader2.page.box_type import BoxType
from OCRReader2.settings.settings_tab import SettingLayout, SettingsTab, SettingType


class ProjectSettingsTab(SettingsTab):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.box_type_list: Optional[QListWidget] = None
        self.langs_list: Optional[QListWidget] = None

        self.settings_layouts = [
            SettingLayout(
                category="OCR",
                key="ppi",
                setting_type=SettingType.SPINBOX_INT,
                label="PPI:",
                action=lambda: self.update_spinbox_int_setting("ppi"),
                data_type=int,
                bottom=0,
                top=9999,
            ),
            SettingLayout(
                category="OCR",
                key="paper_size",
                setting_type=SettingType.COMBOBOX,
                label="Paper Size:",
                action=lambda: self.update_combobox_setting("paper_size"),
            ),
            SettingLayout(
                category="OCR",
                key="layout_analyzer",
                setting_type=SettingType.COMBOBOX,
                label="Layout Analyzer:",
                action=lambda: self.update_combobox_setting("layout_analyzer"),
                data_type=str,
            ),
            SettingLayout(
                category="OCR Editor",
                key="x_size_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="X Size Threshold:",
                action=lambda: self.update_spinbox_int_setting("x_size_threshold"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="OCR Editor",
                key="y_size_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="Y Size Threshold:",
                action=lambda: self.update_spinbox_int_setting("y_size_threshold"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="OCR Editor",
                key="padding",
                setting_type=SettingType.SPINBOX_INT,
                label="Padding:",
                action=lambda: self.update_spinbox_int_setting("padding"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="OCR Editor",
                key="box_types",
                setting_type=SettingType.TABLE,
                label="Box Types:",
                action=lambda: self.update_box_types(),
            ),
            SettingLayout(
                category="OCR Editor",
                key="langs",
                setting_type=SettingType.TABLE,
                label="Languages:",
                action=lambda: self.update_langs(),
            ),
            SettingLayout(
                category="Export",
                key="export_path",
                setting_type=SettingType.FOLDER,
                label="Export Path:",
                action=lambda: self.update_line_edit_setting("export_path"),
            ),
            SettingLayout(
                category="Export",
                key="export_preview_path",
                setting_type=SettingType.FOLDER,
                label="Export Preview Path:",
                action=lambda: self.update_line_edit_setting("export_preview_path"),
            ),
            SettingLayout(
                category="Tesseract",
                key="tesseract_options",
                setting_type=SettingType.EDIT_TEXT,
                label="Tesseract Options:",
                action=lambda: self.update_line_edit_setting("tesseract_options"),
            ),
            SettingLayout(
                category="Tesseract",
                key="tesseract_data_path",
                setting_type=SettingType.FOLDER,
                label="Tesseract Data Path:",
                action=lambda: self.update_line_edit_setting("tesseract_data_path"),
            ),
        ]

        self.create_layout()

    def create_table_layout(self, setting: SettingLayout) -> QLayout:
        table_widget = self.create_table(setting)

        layout = self.create_vertical_layout()
        layout.addWidget(QLabel(setting.label))
        layout.addWidget(table_widget)

        # Store the table widget in the setting elements for later access
        self.setting_elements[setting.key] = table_widget

        return layout

    def create_table(self, setting: SettingLayout) -> QWidget:
        if setting.key == "box_types":
            self.box_type_list = QListWidget(self)
            self.box_type_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            self.box_type_list.itemChanged.connect(self.update_box_types)
            return self.box_type_list
        elif setting.key == "langs":
            self.langs_list = QListWidget(self)
            self.langs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            self.langs_list.itemChanged.connect(self.update_langs)
            return self.langs_list

        return QWidget(self)

    def load_settings(
        self,
        application_settings: SettingsManager,
        available_langs: Optional[List[Lang]] = None,
    ) -> None:
        self.settings = application_settings

        # Load SPINBOX_INT settings
        self.load_spinbox_int_setting("ppi", 0)
        self.load_spinbox_int_setting("x_size_threshold", 0)
        self.load_spinbox_int_setting("y_size_threshold", 0)
        self.load_spinbox_int_setting("padding", 0)

        # Load COMBOBOX settings
        sizes = list(SIZES.keys())
        self.fill_combo_box("paper_size", sizes)
        self.load_combobox_setting("paper_size", sizes[0])

        self.fill_combo_box(
            "layout_analyzer",
            list(ANALYZER_REGISTRY.keys()),
        )
        self.load_combobox_setting(
            "layout_analyzer",
            next(iter(ANALYZER_REGISTRY.keys()), ""),
        )

        # Load FOLDER settings
        self.load_folder_setting("export_path", "")
        self.load_folder_setting("export_preview_path", "")
        self.load_folder_setting("tesseract_data_path", "")

        # Load EDIT_TEXT settings
        self.load_line_edit_setting("tesseract_options", "")

        # Load TABLE settings
        self.load_table_setting("box_types", [box_type.value for box_type in BoxType])
        if available_langs is not None:
            self.load_table_setting(
                "langs", [Lang(lang.name).pt2t for lang in available_langs]
            )

    def load_table_setting(self, key: str, default_values: List[str]) -> None:
        if self.settings is None:
            return

        if key == "box_types" and self.box_type_list is not None:
            self.box_type_list.clear()
            box_types = self.settings.get(key, default_values)
            for box_type in BoxType:
                item = QListWidgetItem(box_type.value)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if box_type.value in box_types:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
                self.box_type_list.addItem(item)
        elif key == "langs" and self.langs_list is not None:
            self.langs_list.clear()
            langs = self.settings.get(key, default_values)
            for lang in default_values:
                item = QListWidgetItem(lang)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if lang in langs:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
                self.langs_list.addItem(item)

    def update_box_types(self) -> None:
        if self.box_type_list is None:
            return

        if self.settings:
            box_types = [
                self.box_type_list.item(i).text()
                for i in range(self.box_type_list.count())
                if self.box_type_list.item(i).checkState() == Qt.CheckState.Checked
            ]
            self.settings.set("box_types", box_types)

    def update_langs(self) -> None:
        if self.langs_list is None:
            return

        if self.settings:
            langs = [
                self.langs_list.item(i).text()
                for i in range(self.langs_list.count())
                if self.langs_list.item(i).checkState() == Qt.CheckState.Checked
            ]
            self.settings.set("langs", langs)
