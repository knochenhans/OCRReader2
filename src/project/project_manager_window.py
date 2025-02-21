from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QListWidget,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from project.project_manager import ProjectManager  # type: ignore


class ProjectManagerWindow(QDialog):
    project_opened = Signal()

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setWindowTitle("Project Manager")
        self.setGeometry(300, 300, 600, 400)

        self.main_layout = QVBoxLayout(self)

        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_project)
        self.main_layout.addWidget(self.project_list)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.open_button = QPushButton("Open Project")
        self.open_button.clicked.connect(self.open_project)
        self.button_layout.addWidget(self.open_button)

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
        for project in self.project_manager.projects:
            self.project_list.addItem(f"{project.name} ({project.uuid})")

    def open_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No project selected")
            return
        selected_item = selected_items[0]
        project_uuid = selected_item.text().split("(")[-1].strip(")")
        project = self.project_manager.get_project_by_uuid(project_uuid)
        if project:
            self.project_manager.current_project = project
            self.project_opened.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Project not found")

    def remove_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No project selected")
            return
        selected_item = selected_items[0]
        project_uuid = selected_item.text().split("(")[-1].strip(")")
        project = self.project_manager.get_project_by_uuid(project_uuid)
        if project:
            index = self.project_manager.projects.index(project)
            self.project_manager.remove_project(index)
            self.refresh_project_list()
            QMessageBox.information(
                self, "Project Removed", f"Removed project: {project.name}"
            )
        else:
            QMessageBox.warning(self, "Warning", "Project not found")

    def import_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Project", "", "Project Files (*.proj)"
        )
        if file_path:
            self.project_manager.import_project(file_path)
            self.refresh_project_list()
            QMessageBox.information(
                self, "Project Imported", "Project imported successfully"
            )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
