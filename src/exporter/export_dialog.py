from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QMessageBox,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
from loguru import logger

from project.project import EXPORTER_MAP, Project  # type: ignore
from project.project import ExporterType  # type: ignore


class ExporterPreviewDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)

        self.project = project
        self.export_path = ""

        self.setWindowTitle("Exporter Preview")
        self.setGeometry(300, 300, 800, 600)

        self.main_layout = QVBoxLayout(self)

        self.exporter_combo_box = QComboBox()
        self.exporter_combo_box.addItems(["EPUB", "HTML", "HTML_SIMPLE", "TXT", "ODT"])
        self.main_layout.addWidget(self.exporter_combo_box)

        self.button_layout = QHBoxLayout()

        self.set_path_button = QPushButton("Set Export Path")
        self.set_path_button.clicked.connect(self.choose_export_path)
        self.button_layout.addWidget(self.set_path_button)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_project)
        self.button_layout.addWidget(self.export_button)

        self.main_layout.addLayout(self.button_layout)

        self.export_path_label = QLabel("No export path set")
        self.main_layout.addWidget(self.export_path_label)

        self.preview_web_view = QWebEngineView()
        self.main_layout.addWidget(self.preview_web_view)

        self.generate_preview()

        self.set_export_path(self.project.project_settings.get("export_path"))

    def generate_preview(self):
        try:
            self.project.export_preview()
            preview_file = os.path.join(
                self.project.project_settings.get("export_preview_path"),
                f"{self.project.name}.html",
            )
            self.preview_web_view.setUrl(f"file:///{preview_file}")
        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate preview: {e}")

    def choose_export_path(self):
        options = QFileDialog.Option()
        file_filter = "All Files (*);;EPUB Files (*.epub);;HTML Files (*.html);;Text Files (*.txt);;ODT Files (*.odt)"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Set Export Path", "", file_filter, options=options
        )
        if file_path:
            self.set_export_path(file_path)

    def set_export_path(self, path: str):
        self.export_path = path
        self.export_path_label.setText(f"Export Path: {self.export_path}")

    def export_project(self):
        if not self.export_path:
            QMessageBox.warning(self, "Warning", "Please set the export path first.")
            return

        # path = os.path.dirname(self.export_path)
        # filename = os.path.basename(self.export_path)

        exporter_type = ExporterType[self.exporter_combo_box.currentText()]
        try:
            self.project.export(exporter_type)
            QMessageBox.information(
                self, "Success", f"Project exported as {exporter_type}"
            )
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export project: {e}")
