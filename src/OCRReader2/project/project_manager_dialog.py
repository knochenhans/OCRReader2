from datetime import datetime
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from OCRReader2.project.new_project_dialog import NewProjectDialog
from OCRReader2.project.project import Project
from OCRReader2.project.project_manager import ProjectManager


class ProjectManagerDialog(QDialog):
    project_opened = Signal()

    def __init__(
        self,
        project_manager: ProjectManager,
        parent: Optional[QWidget] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        super().__init__(parent)
        self.project_manager = project_manager
        self.progress_callback = progress_callback

        self.current_project_uuid = None

        self.setWindowTitle("Project Manager")
        self.setGeometry(300, 300, 800, 400)

        # Main layout with splitter
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.main_layout.addWidget(self.splitter)

        # Left: Project list
        self.project_list = QListWidget()
        self.project_list.itemSelectionChanged.connect(self.update_metadata)
        self.project_list.itemDoubleClicked.connect(self.open_project)
        self.splitter.addWidget(self.project_list)

        # Right: Metadata widget
        self.metadata_widget = QGroupBox("Project Metadata")
        self.metadata_layout = QGridLayout(self.metadata_widget)

        # Align the metadata widget to the top
        self.metadata_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Editable fields for metadata
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.metadata_layout.addWidget(self.name_label, 0, 0)
        self.metadata_layout.addWidget(self.name_edit, 0, 1)

        self.description_label = QLabel("Description:")
        self.description_edit = QLineEdit()
        self.metadata_layout.addWidget(self.description_label, 1, 0)
        self.metadata_layout.addWidget(self.description_edit, 1, 1)

        # Read-only fields for metadata
        self.uuid_label = QLabel("UUID:")
        self.uuid_edit = QLineEdit()
        self.uuid_edit.setReadOnly(True)
        self.metadata_layout.addWidget(self.uuid_label, 2, 0)
        self.metadata_layout.addWidget(self.uuid_edit, 2, 1)

        self.creation_date_label = QLabel("Creation Date:")
        self.creation_date_edit = QLineEdit()
        self.creation_date_edit.setReadOnly(True)
        self.metadata_layout.addWidget(self.creation_date_label, 3, 0)
        self.metadata_layout.addWidget(self.creation_date_edit, 3, 1)

        self.modification_date_label = QLabel("Modification Date:")
        self.modification_date_value = QLineEdit()
        self.modification_date_value.setReadOnly(True)
        self.metadata_layout.addWidget(self.modification_date_label, 4, 0)
        self.metadata_layout.addWidget(self.modification_date_value, 4, 1)

        self.page_count_label = QLabel("Number of Pages:")
        self.page_count_value = QLineEdit()
        self.page_count_value.setReadOnly(True)
        self.metadata_layout.addWidget(self.page_count_label, 5, 0)
        self.metadata_layout.addWidget(self.page_count_value, 5, 1)

        self.splitter.addWidget(self.metadata_widget)

        # Buttons below the splitter
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.open_button = QPushButton("Open Project")
        self.open_button.clicked.connect(self.open_project)
        self.button_layout.addWidget(self.open_button)

        self.new_button = QPushButton("New Project")
        self.new_button.clicked.connect(self.new_project)
        self.button_layout.addWidget(self.new_button)

        self.remove_button = QPushButton("Remove Project")
        self.remove_button.clicked.connect(self.remove_project)
        self.button_layout.addWidget(self.remove_button)

        self.import_button = QPushButton("Import Project")
        self.import_button.clicked.connect(self.import_project)
        self.button_layout.addWidget(self.import_button)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.refresh_project_list)
        self.button_layout.addWidget(self.refresh_button)

        self.refresh_project_list()

        if self.project_list.count() > 0:
            self.project_list.setCurrentRow(0)

    def refresh_project_list(self):
        self.project_list.clear()
        projects = [
            (name, uuid, modification_date)
            for name, uuid, modification_date in self.project_manager.projects
        ]

        # Sort projects by modification_date (newest first)
        projects.sort(
            key=lambda x: (
                datetime.fromisoformat(x[2])
                if isinstance(x[2], str) and x[2]
                else datetime.min
            ),
            reverse=True,
        )
        for name, uuid, modification_date in projects:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, uuid)
            self.project_list.addItem(item)

    def update_metadata(self):
        # Save metadata for the previously selected project
        if self.current_project_uuid:
            metadata = {
                "name": self.name_edit.text().strip(),
                "description": self.description_edit.text().strip(),
            }
            self.project_manager.save_metadata(self.current_project_uuid, metadata)

        # Update metadata for the newly selected project
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            self.name_edit.clear()
            self.description_edit.clear()
            self.creation_date_edit.clear()
            self.modification_date_value.clear()
            self.page_count_value.clear()  # Clear page count
            self.current_project_uuid = None
            return

        selected_item = selected_items[0]
        project_uuid = selected_item.data(Qt.ItemDataRole.UserRole)
        metadata = self.project_manager.load_metadata(project_uuid)

        if metadata:
            self.name_edit.setText(metadata.get("name", ""))
            self.description_edit.setText(metadata.get("description", ""))
            creation_date = metadata.get("creation_date", "")
            modification_date = metadata.get("modification_date", "")
            page_count = self.project_manager.get_page_count(project_uuid)
            try:
                if creation_date:
                    creation_date = datetime.fromisoformat(creation_date).strftime(
                        "%B %d, %Y %H:%M:%S"
                    )
                if modification_date:
                    modification_date = datetime.fromisoformat(
                        modification_date
                    ).strftime("%B %d, %Y %H:%M:%S")
            except ValueError:
                pass
            self.creation_date_edit.setText(creation_date)
            self.modification_date_value.setText(modification_date)
            self.page_count_value.setText(str(page_count))
            self.uuid_edit.setText(project_uuid)
            self.current_project_uuid = project_uuid
        else:
            self.name_edit.clear()
            self.description_edit.clear()
            self.creation_date_edit.clear()
            self.modification_date_value.clear()
            self.page_count_value.clear()
            self.uuid_edit.clear()
            self.current_project_uuid = None

    def open_project(self, clicked_item: Optional[QListWidgetItem] = None):
        if clicked_item:
            selected_items = [clicked_item]
        else:
            selected_items = self.project_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "Warning", "No project selected")
            return
        selected_item = selected_items[0]
        project_uuid = selected_item.data(Qt.ItemDataRole.UserRole)
        project = self.project_manager.load_project(
            project_uuid, self.progress_callback
        )
        self.open_project_(project)

    def remove_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No project selected")
            return
        selected_item = selected_items[0]
        project_uuid = selected_item.data(Qt.ItemDataRole.UserRole)
        self.project_manager.projects = [
            (name, uuid, modification_date)
            for name, uuid, modification_date in self.project_manager.projects
            if uuid != project_uuid
        ]
        self.refresh_project_list()

    def import_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Project", "", "Project Files (*.proj)"
        )
        if file_path:
            self.project_manager.import_project(file_path)
            self.refresh_project_list()

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_name, description = dialog.get_project_details()
            if project_name:
                new_project = self.project_manager.new_project(
                    project_name, description, creation_date=datetime.now()
                )

                self.refresh_project_list()
                self.open_project_(new_project)
            else:
                QMessageBox.warning(self, "Warning", "Project name cannot be empty.")

    def open_project_(self, project: Project) -> None:
        self.project_manager.current_project = project
        self.project_opened.emit()
        self.accept()

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        if arg__1.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(arg__1)
