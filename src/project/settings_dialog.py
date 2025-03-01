from typing import List
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QDialogButtonBox,
)

from PySide6.QtCore import Signal, Qt

from project.project_settings import ProjectSettings  # type: ignore
from iso639 import Lang  # type: ignore
from papersize import SIZES  # type: ignore
from page.box_type import BoxType  # type: ignore


class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.project_settings = ProjectSettings()
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 800)

        layout: QVBoxLayout = QVBoxLayout(self)

        tab_widget: QTabWidget = QTabWidget(self)
        layout.addWidget(tab_widget)

        # General Options Tab
        general_tab: QWidget = QWidget()
        tab_widget.addTab(general_tab, "General Options")

        # Project Options Tab
        project_tab: QWidget = QWidget()
        project_layout: QFormLayout = QFormLayout(project_tab)

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

        self.export_scaling_factor_spinbox: QDoubleSpinBox = QDoubleSpinBox()
        self.export_scaling_factor_spinbox.valueChanged.connect(
            self.update_export_scaling_factor
        )
        project_layout.addRow(
            "Export Scaling Factor:", self.export_scaling_factor_spinbox
        )

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

        tab_widget.addTab(project_tab, "Project Options")

        # Add OK and Cancel buttons
        button_box: QDialogButtonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)

        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)

    def load_settings(
        self, project_settings: ProjectSettings, available_langs: List[Lang]
    ):
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
        self.export_scaling_factor_spinbox.setValue(
            self.project_settings.settings.get("export_scaling_factor", 1.0)
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

    def update_x_size_threshold(self, value: int):
        self.project_settings.settings["x_size_threshold"] = value

    def update_y_size_threshold(self, value: int):
        self.project_settings.settings["y_size_threshold"] = value

    def update_ppi(self, value: int):
        self.project_settings.settings["ppi"] = value

    def update_langs(self):
        langs = [
            Lang(self.langs_list.item(i).text()).pt2t
            for i in range(self.langs_list.count())
            if self.langs_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.project_settings.settings["langs"] = langs

    def update_paper_size(self, value: str):
        self.project_settings.settings["paper_size"] = value

    def update_export_scaling_factor(self, value: float):
        self.project_settings.settings["export_scaling_factor"] = value

    def update_export_path(self, value: str):
        self.project_settings.settings["export_path"] = value

    def update_export_preview_path(self, value: str):
        self.project_settings.settings["export_preview_path"] = value

    def update_box_types(self):
        box_types = [
            self.box_type_list.item(i).text()
            for i in range(self.box_type_list.count())
            if self.box_type_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.project_settings.settings["box_types"] = box_types

    def on_ok_clicked(self):
        self.settings_changed.emit()
        self.accept()
