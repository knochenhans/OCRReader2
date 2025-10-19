from datetime import datetime
from typing import Any, Dict

from PySide6.QtWidgets import QFileDialog, QWidget

from OCRReader2.exporter.export_dialog import ExporterPreviewDialog
from OCRReader2.main_window.page_actions import PageActions
from OCRReader2.main_window.page_icon_view import PagesIconView
from OCRReader2.page_editor.page_editor_view import PageEditorView
from OCRReader2.project.project import Project
from OCRReader2.project.project_manager import ProjectManager


class ProjectActions:
    def __init__(
        self,
        main_window: QWidget,
        project_manager: ProjectManager,
        page_icon_view: PagesIconView,
        page_editor_view: PageEditorView,
        page_actions: PageActions,
    ) -> None:
        self.main_window = main_window
        self.project_manager = project_manager
        self.page_icon_view = page_icon_view
        self.page_editor_view = page_editor_view
        self.page_actions = page_actions

    def open_project(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Project File",
            "",
            "Project Files (*.proj);;All Files (*)",
        )
        if file_name:
            project_uuid = self.project_manager.import_project(file_name)
            self.project_manager.load_project(
                project_uuid, self.main_window.update_progress_bar
            )
            self.load_current_project()

    def load_current_project(self) -> None:
        project: Project = self.project_manager.current_project

        if not project:
            return

        self.main_window.show_status_message(f"Loading project: {project.uuid}")

        if not project.settings_manager:
            return

        for index, page in enumerate(project.pages):
            page_data: Dict[str, Any] = {
                "number": index + 1,
            }
            if page.image_path:
                self.page_icon_view.add_page(page.image_path, page_data)
            self.main_window.update_progress_bar(index + 1, len(project.pages))

        self.page_actions.open_page(project.settings_manager.get("current_page_index", 0))

        self.main_window.project_name_label.setText(f"Current project: {project.name}")
        self.page_editor_view.project_settings_manager = project.settings_manager
        self.page_editor_view.set_zoom(project.settings_manager.get("zoom_level", 1.0))
        self.main_window.exporter_widget.set_project(project)

        self.main_window.box_ids_flagged_for_training = (
            self.project_manager.current_project.settings_manager.get("flagged_box_ids", [])
        )

    def save_project(self):
        self.main_window.show_status_message("Saving project")
        if self.project_manager.current_project:
            self.project_manager.current_project.settings_manager.set(
                "current_page_index", self.page_icon_view.get_current_page_index()
            )
            self.project_manager.current_project.settings_manager.set(
                "zoom_level", self.page_editor_view.current_zoom
            )
            self.project_manager.current_project.modification_date = datetime.now()

        self.project_manager.save_current_project(self.main_window.update_progress_bar)
        self.main_window.show_status_message("Project saved")

    def close_project(self):
        self.main_window.show_status_message("Closing project")
        self.project_manager.close_current_project()
        self.page_icon_view.clear()
        self.page_editor_view.clear_page()
        self.main_window.update()
        self.main_window.show_project_manager_dialog()

    def export_project(self) -> None:
        self.main_window.show_status_message("Exporting project")
        project = self.project_manager.current_project

        if not project:
            return

        exporter_dialog = ExporterPreviewDialog(
            project, self.main_window.application_settings, self.main_window
        )
        exporter_dialog.exec()

    def analyze_project(self) -> None:
        self.main_window.show_status_message("Analyzing project")
        project = self.project_manager.current_project

        if not project:
            return

        from PySide6.QtWidgets import (
            QInputDialog,
        )

        start_page, ok = QInputDialog.getInt(
            self.main_window,
            "Select Start Page",
            "Enter the start page number:",
            1,
            1,
            len(project.pages),
        )

        if not ok:
            self.main_window.show_status_message("Analysis canceled")
            return

        for index, page in enumerate(project.pages[start_page - 1 :], start=start_page):
            page.analyze_page(project.settings_manager)
            self.main_window.update_progress_bar(index, len(project.pages))

        self.main_window.show_status_message("Project analyzed")
