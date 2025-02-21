from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
import logging

from project.project import Project  # type: ignore

logger = logging.getLogger(__name__)


class ExporterPreviewDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)

        self.project = project

        self.setWindowTitle("Exporter Preview")
        self.setGeometry(300, 300, 800, 600)

        self.main_layout = QVBoxLayout(self)

        self.preview_web_view = QWebEngineView()
        self.main_layout.addWidget(self.preview_web_view)

        self.generate_preview()

    def generate_preview(self):
        try:
            self.project.export_preview()
            preview_file = os.path.join(
                self.project.settings.get("export_preview_path"),
                f"{self.project.name}.html",
            )
            self.preview_web_view.setUrl(f"file:///{preview_file}")
        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate preview: {e}")
