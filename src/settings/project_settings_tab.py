from typing import List, Optional
from PySide6.QtWidgets import QWidget, QListWidgetItem, QLabel, QListWidget
from PySide6.QtCore import Qt
from settings.settings import Settings  # type: ignore
from settings.settings_tab import SettingsTab, SettingType, SettingLayout  # type: ignore
from iso639 import Lang
from papersize import SIZES  # type: ignore
from page.box_type import BoxType  # type: ignore


class ProjectSettingsTab(SettingsTab):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.box_type_list: Optional[QListWidget] = None
        self.langs_list: Optional[QListWidget] = None

        self.settings_layouts: List[SettingLayout] = [
            SettingLayout(
                category="Project Settings",
                key="ppi",
                setting_type=SettingType.SPINBOX_INT,
                label="PPI:",
                action=lambda: self.update_spinbox_int_setting("ppi"),
                data_type=int,
                bottom=0,
                top=9999,
            ),
            SettingLayout(
                category="Project Settings",
                key="x_size_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="X Size Threshold:",
                action=lambda: self.update_spinbox_int_setting("x_size_threshold"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="Project Settings",
                key="y_size_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="Y Size Threshold:",
                action=lambda: self.update_spinbox_int_setting("y_size_threshold"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="Project Settings",
                key="padding",
                setting_type=SettingType.SPINBOX_INT,
                label="Padding:",
                action=lambda: self.update_spinbox_int_setting("padding"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="Project Settings",
                key="paper_size",
                setting_type=SettingType.COMBOBOX,
                label="Paper Size:",
                action=lambda: self.update_combobox_setting("paper_size"),
            ),
            SettingLayout(
                category="Project Settings",
                key="export_path",
                setting_type=SettingType.FOLDER,
                label="Export Path:",
                action=lambda: self.update_line_edit_setting("export_path"),
            ),
            SettingLayout(
                category="Project Settings",
                key="export_preview_path",
                setting_type=SettingType.FOLDER,
                label="Export Preview Path:",
                action=lambda: self.update_line_edit_setting("export_preview_path"),
            ),
            SettingLayout(
                category="Project Settings",
                key="tesseract_options",
                setting_type=SettingType.EDIT_TEXT,
                label="Tesseract Options:",
                action=lambda: self.update_line_edit_setting("tesseract_options"),
            ),
            SettingLayout(
                category="Project Settings",
                key="box_types",
                setting_type=SettingType.TABLE,
                label="Box Types:",
                action=lambda: self.update_box_types(),
            ),
            SettingLayout(
                category="Project Settings",
                key="langs",
                setting_type=SettingType.TABLE,
                label="Languages:",
                action=lambda: self.update_langs(),
            ),
        ]

        self.create_layout()

    def create_table_layout(self, setting: SettingLayout) -> QWidget:
        table_widget = self.create_table(setting)

        layout = QWidget()
        layout_layout = self.create_vertical_layout()
        layout_layout.addWidget(QLabel(setting.label))
        layout_layout.addWidget(table_widget)
        layout.setLayout(layout_layout)

        # Store the table widget in the setting elements for later access
        self.setting_elements[setting.key] = table_widget

        return layout

    def create_table(self, setting: SettingLayout) -> QWidget:
        from PySide6.QtWidgets import QListWidget

        table_widget = QListWidget(self)
        table_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        if setting.key == "box_types":
            for box_type in BoxType:
                item = QListWidgetItem(box_type.value)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                table_widget.addItem(item)
        elif setting.key == "langs":
            for lang in setting.action() or []:
                item = QListWidgetItem(lang)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                table_widget.addItem(item)

        return table_widget

    def load_settings(
        self, project_settings: Settings, available_langs: List[Lang]
    ) -> None:
        self.settings = project_settings

        # Load SPINBOX_INT settings
        self.load_spinbox_int_setting("ppi", 0)
        self.load_spinbox_int_setting("x_size_threshold", 0)
        self.load_spinbox_int_setting("y_size_threshold", 0)
        self.load_spinbox_int_setting("padding", 0)

        # Load COMBOBOX settings
        sizes = list(SIZES.keys())
        self.fill_combo_box("paper_size", sizes)
        self.load_combobox_setting("paper_size", sizes[0])

        # Load FOLDER settings
        self.load_folder_setting("export_path", "")
        self.load_folder_setting("export_preview_path", "")

        # Load EDIT_TEXT settings
        self.load_line_edit_setting("tesseract_options", "")

        # Load TABLE settings
        self.load_table_setting("box_types", [box_type.value for box_type in BoxType])
        self.load_table_setting(
            "langs", [Lang(lang.name).pt2t for lang in available_langs]
        )

    def load_table_setting(self, key: str, default_values: List[str]) -> None:
        if self.box_type_list is None or self.langs_list is None:
            return

        if key == "box_types":
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
        elif key == "langs":
            self.langs_list.clear()
            langs = self.settings.get(key, default_values)
            for lang in langs:
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
