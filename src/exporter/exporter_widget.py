import os
from typing import Optional

from loguru import logger
from pathvalidate import sanitize_filename
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from project.project import ExporterType, Project  # type: ignore
from settings.settings import Settings  # type: ignore


class ExporterWidget(QWidget):
    def __init__(
        self, application_settings: Settings, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.application_settings: Settings = application_settings

        self.project: Optional[Project] = None
        self.export_path: str = ""

        self.main_layout: QVBoxLayout = QVBoxLayout(self)

        self.preview_web_view: QWebEngineView = QWebEngineView()
        self.preview_web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.preview_web_view)

        self.exporter_combo_box: QComboBox = QComboBox()
        self.exporter_mapping: dict[str, ExporterType] = {
            "Simple HTML": ExporterType.HTML_SIMPLE,
            "EPUB": ExporterType.EPUB,
            "Detailed HTML": ExporterType.HTML,
            "Plain Text": ExporterType.TXT,
            "OpenDocument Text": ExporterType.ODT,
        }
        self.exporter_combo_box.addItems(list(self.exporter_mapping.keys()))
        self.main_layout.addWidget(self.exporter_combo_box)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        self.set_path_button: QPushButton = QPushButton("Set Export Path")
        self.set_path_button.clicked.connect(self.choose_export_path)
        self.button_layout.addWidget(self.set_path_button)

        self.export_button: QPushButton = QPushButton("Export")
        self.export_button.clicked.connect(self.export_project)
        self.button_layout.addWidget(self.export_button)

        self.refresh_preview_button: QPushButton = QPushButton("Refresh Preview")
        self.refresh_preview_button.clicked.connect(self.generate_preview)
        self.button_layout.addWidget(self.refresh_preview_button)

        self.main_layout.addLayout(self.button_layout)

        self.export_path_label: QLabel = QLabel("No export path set")
        self.main_layout.addWidget(self.export_path_label)

    def set_project(self, project: Project) -> None:
        self.project = project
        if self.project.settings:
            self.set_export_path(self.project.settings.get("export_path"))
            self.filename: str = sanitize_filename(self.project.name)
            self.generate_preview()

    def generate_preview(self) -> None:
        if not self.project:
            logger.error("Project is not set")
            return
        try:
            self.project.export_preview(self.application_settings)

            if self.project.settings:
                export_path: str = self.project.settings.get("export_preview_path")
                
                if not export_path:
                    logger.error("Export preview path is not set")
                    return
                
                preview_file: str = os.path.join(
                    export_path,
                    f"{self.filename}.html",
                )
                self.preview_web_view.setUrl(f"file:///{preview_file}")
        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate preview: {e}")

    def choose_export_path(self) -> None:
        file_filter: str = (
            "All Files (*);;EPUB Files (*.epub);;HTML Files (*.html);;Text Files (*.txt);;ODT Files (*.odt)"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Set Export Path", "", file_filter
        )
        if file_path:
            self.set_export_path(file_path)

    def set_export_path(self, path: str) -> None:
        self.export_path = path
        self.export_path_label.setText(f"Export Path: {self.export_path}")

    def export_project(self) -> None:
        if not self.project:
            QMessageBox.warning(self, "Warning", "Project is not set.")
            return

        if not self.export_path:
            QMessageBox.warning(self, "Warning", "Please set the export path first.")
            return

        exporter_name: str = self.exporter_combo_box.currentText()
        exporter_type: ExporterType = self.exporter_mapping[exporter_name]
        try:
            self.project.export(exporter_type, self.application_settings)
            QMessageBox.information(
                self, "Success", f"Project exported as {exporter_type}"
            )
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export project: {e}")
