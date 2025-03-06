from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QMessageBox,
    QWidget,
    QSizePolicy,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
from loguru import logger
from pathvalidate import sanitize_filename

from project.project import Project, ExporterType  # type: ignore


class ExporterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.project = None
        self.export_path = ""

        self.main_layout = QVBoxLayout(self)

        self.preview_web_view = QWebEngineView()
        self.preview_web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.preview_web_view)

        self.exporter_combo_box = QComboBox()
        self.exporter_mapping = {
            "Simple HTML": ExporterType.HTML_SIMPLE,
            "EPUB": ExporterType.EPUB,
            "Detailed HTML": ExporterType.HTML,
            "Plain Text": ExporterType.TXT,
            "OpenDocument Text": ExporterType.ODT,
        }
        self.exporter_combo_box.addItems(list(self.exporter_mapping.keys()))
        self.main_layout.addWidget(self.exporter_combo_box)

        self.button_layout = QHBoxLayout()

        self.set_path_button = QPushButton("Set Export Path")
        self.set_path_button.clicked.connect(self.choose_export_path)
        self.button_layout.addWidget(self.set_path_button)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_project)
        self.button_layout.addWidget(self.export_button)

        self.refresh_preview_button = QPushButton("Refresh Preview")
        self.refresh_preview_button.clicked.connect(self.generate_preview)
        self.button_layout.addWidget(self.refresh_preview_button)

        self.main_layout.addLayout(self.button_layout)

        self.export_path_label = QLabel("No export path set")
        self.main_layout.addWidget(self.export_path_label)

    def set_project(self, project: Project):
        self.project = project
        self.set_export_path(self.project.settings.get("export_path"))
        self.filename = sanitize_filename(self.project.name)
        self.generate_preview()

    def generate_preview(self):
        if not self.project:
            logger.error("Project is not set")
            return
        try:
            self.project.export_preview()
            preview_file = os.path.join(
                self.project.settings.get("export_preview_path"),
                f"{self.filename}.html",
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
        if not self.project:
            QMessageBox.warning(self, "Warning", "Project is not set.")
            return

        if not self.export_path:
            QMessageBox.warning(self, "Warning", "Please set the export path first.")
            return

        exporter_name = self.exporter_combo_box.currentText()
        exporter_type = self.exporter_mapping[exporter_name]
        try:
            self.project.export(exporter_type)
            QMessageBox.information(
                self, "Success", f"Project exported as {exporter_type}"
            )
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export project: {e}")
