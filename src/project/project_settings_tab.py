from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
)
from typing import List, Optional

from settings import Settings  # type: ignore
from iso639 import Lang
from papersize import SIZES  # type: ignore
from page.box_type import BoxType  # type: ignore


class ProjectSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.project_settings: Optional[Settings] = None
        self.init_ui()

    def init_ui(self) -> None:
        project_layout: QFormLayout = QFormLayout(self)

        self.ppi_spinbox: QSpinBox = QSpinBox()
        self.ppi_spinbox.setRange(0, 9999)
        self.ppi_spinbox.valueChanged.connect(self.update_ppi)
        project_layout.addRow("PPI:", self.ppi_spinbox)

        self.langs_list: QListWidget = QListWidget()
        self.langs_list.itemChanged.connect(self.update_langs)
        project_layout.addRow("Languages:", self.langs_list)

        self.paper_size_combobox: QComboBox = QComboBox()
        self.paper_size_combobox.addItems(list(SIZES.keys()))
        self.paper_size_combobox.currentTextChanged.connect(self.update_paper_size)
        project_layout.addRow("Paper Size:", self.paper_size_combobox)

        self.export_path_lineedit: QLineEdit = QLineEdit()
        self.export_path_lineedit.textChanged.connect(self.update_export_path)
        project_layout.addRow("Export Path:", self.export_path_lineedit)

        self.export_preview_path_lineedit: QLineEdit = QLineEdit()
        self.export_preview_path_lineedit.textChanged.connect(
            self.update_export_preview_path
        )
        project_layout.addRow("Export Preview Path:", self.export_preview_path_lineedit)

        # BoxType Options
        self.box_type_list: QListWidget = QListWidget()
        self.box_type_list.itemChanged.connect(self.update_box_types)
        project_layout.addRow("Box Types:", self.box_type_list)

        # X/Y Size Thresholds
        self.x_size_threshold_spinbox: QSpinBox = QSpinBox()
        self.x_size_threshold_spinbox.valueChanged.connect(self.update_x_size_threshold)
        project_layout.addRow("X Size Threshold:", self.x_size_threshold_spinbox)

        self.y_size_threshold_spinbox: QSpinBox = QSpinBox()
        self.y_size_threshold_spinbox.valueChanged.connect(self.update_y_size_threshold)
        project_layout.addRow("Y Size Threshold:", self.y_size_threshold_spinbox)

        # Padding Option
        self.padding_spinbox: QSpinBox = QSpinBox()
        self.padding_spinbox.setRange(0, 1000)
        self.padding_spinbox.valueChanged.connect(self.update_padding)
        project_layout.addRow("Padding:", self.padding_spinbox)

        # Tesseract Options
        self.tesseract_options_edit: QLineEdit = QLineEdit()
        self.tesseract_options_edit.textChanged.connect(self.update_tesseract_options)
        project_layout.addRow("Tesseract Options:", self.tesseract_options_edit)

    def load_settings(
        self, project_settings: Settings, available_langs: List[Lang]
    ) -> None:
        self.project_settings = project_settings
        self.ppi_spinbox.setValue(self.project_settings.settings.get("ppi", 0))

        self.langs_list.clear()

        for lang in available_langs:
            item = QListWidgetItem(lang.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if Lang(lang.name).pt2t in self.project_settings.settings.get("langs", []):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.langs_list.addItem(item)

        self.paper_size_combobox.setCurrentText(
            self.project_settings.settings.get("paper_size", "")
        )
        self.export_path_lineedit.setText(
            self.project_settings.settings.get("export_path", "")
        )
        self.export_preview_path_lineedit.setText(
            self.project_settings.settings.get("export_preview_path", "")
        )
        self.x_size_threshold_spinbox.setValue(
            self.project_settings.settings.get("x_size_threshold", 0)
        )
        self.y_size_threshold_spinbox.setValue(
            self.project_settings.settings.get("y_size_threshold", 0)
        )
        self.padding_spinbox.setValue(self.project_settings.settings.get("padding", 0))

        self.tesseract_options_edit.setText(
            self.project_settings.settings.get("tesseract_options", "")
        )

        if self.project_settings.settings.get("box_types", []) == []:
            self.project_settings.settings["box_types"] = [
                box_type.value for box_type in BoxType
            ]

        self.box_type_list.clear()

        for box_type in BoxType:
            item = QListWidgetItem(box_type.value)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if box_type.value in self.project_settings.settings.get("box_types", []):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.box_type_list.addItem(item)

    def update_x_size_threshold(self, value: int) -> None:
        if self.project_settings:
            self.project_settings.settings["x_size_threshold"] = value

    def update_y_size_threshold(self, value: int) -> None:
        if self.project_settings:
            self.project_settings.settings["y_size_threshold"] = value

    def update_ppi(self, value: int) -> None:
        if self.project_settings:
            self.project_settings.settings["ppi"] = value

    def update_langs(self) -> None:
        if self.project_settings:
            langs: List[str] = [
                Lang(self.langs_list.item(i).text()).pt2t
                for i in range(self.langs_list.count())
                if self.langs_list.item(i).checkState() == Qt.CheckState.Checked
            ]
            self.project_settings.settings["langs"] = langs

    def update_paper_size(self, value: str) -> None:
        if self.project_settings:
            self.project_settings.settings["paper_size"] = value

    def update_export_path(self, value: str) -> None:
        if self.project_settings:
            self.project_settings.settings["export_path"] = value

    def update_export_preview_path(self, value: str) -> None:
        if self.project_settings:
            self.project_settings.settings["export_preview_path"] = value

    def update_box_types(self) -> None:
        if self.project_settings:
            box_types: List[str] = [
                self.box_type_list.item(i).text()
                for i in range(self.box_type_list.count())
                if self.box_type_list.item(i).checkState() == Qt.CheckState.Checked
            ]
            self.project_settings.settings["box_types"] = box_types

    def update_padding(self, value: int) -> None:
        if self.project_settings:
            self.project_settings.settings["padding"] = value

    def update_tesseract_options(self, value: str) -> None:
        if self.project_settings:
            self.project_settings.settings["tesseract_options"] = value
