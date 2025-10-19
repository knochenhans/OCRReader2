from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
)
from SettingsManager import SettingsManager

from OCRReader2.exporter.exporter_widget import ExporterWidget
from OCRReader2.project.project import Project


class ExporterPreviewDialog(QDialog):
    def __init__(
        self,
        project: Project,
        application_settings: SettingsManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.project = project

        self.setWindowTitle("Exporter Preview")
        self.setGeometry(300, 300, 800, 600)

        self.main_widget = ExporterWidget(application_settings, self)
        self.main_widget.set_project(self.project)

        layout = QVBoxLayout()
        layout.addWidget(self.main_widget)
        self.setLayout(layout)
