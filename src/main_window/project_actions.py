from datetime import datetime

from PySide6.QtWidgets import QFileDialog

from exporter.export_dialog import ExporterPreviewDialog  # type: ignore


class ProjectActions:
    def __init__(
        self,
        main_window,
        project_manager,
        page_icon_view,
        page_editor_view,
        page_actions,
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
        project = self.project_manager.current_project

        if not project:
            return

        self.main_window.show_status_message(f"Loading project: {project.uuid}")

        if not project.settings:
            return

        for index, page in enumerate(project.pages):
            page_data = {
                "number": index + 1,
            }
            if page.image_path:
                self.page_icon_view.add_page(page.image_path, page_data)
            self.main_window.update_progress_bar(index + 1, len(project.pages))

        self.page_actions.open_page(project.settings.get("current_page_index", 0))

        self.main_window.project_name_label.setText(f"Current project: {project.name}")
        self.page_editor_view.project_settings = project.settings
        self.page_editor_view.set_zoom(project.settings.get("zoom_level", 1.0))
        self.main_window.exporter_widget.set_project(project)

        self.main_window.box_ids_flagged_for_training = (
            self.project_manager.current_project.settings.get("flagged_box_ids", [])
        )

    def save_project(self):
        self.main_window.show_status_message("Saving project")
        if self.project_manager.current_project:
            self.project_manager.current_project.settings.set(
                "current_page_index", self.page_icon_view.get_current_page_index()
            )
            self.project_manager.current_project.settings.set(
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
