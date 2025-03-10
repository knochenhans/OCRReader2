from typing import List
from PySide6.QtWidgets import QFileDialog
import tempfile

from exporter.export_dialog import ExporterPreviewDialog  # type: ignore
from project.project import Project  # type: ignore


class UserActions:
    def __init__(
        self,
        main_window,
        page_editor_controller,
        project_manager,
        page_icon_view,
        page_editor_view,
    ) -> None:
        from main_window.main_window import MainWindow  # type: ignore
        from page_editor.page_editor_controller import PageEditorController  # type: ignore
        from project.project_manager import ProjectManager  # type: ignore
        from main_window.page_icon_view import PagesIconView  # type: ignore
        from page_editor.page_editor_view import PageEditorView  # type: ignore

        self.main_window: MainWindow = main_window
        self.page_editor_controller: PageEditorController = page_editor_controller
        self.project_manager: ProjectManager = project_manager
        self.page_icon_view: PagesIconView = page_icon_view
        self.page_editor_view: PageEditorView = page_editor_view

    def add_images(self, filenames: List[str]) -> None:
        if self.project_manager.current_project is not None:
            self.project_manager.current_project.add_images(filenames)

    def import_media_files(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Load images",
            "",
            "Images (*.png *.jpg *.jpeg *.pdf)",
        )
        if filenames:
            self.main_window.show_status_message(f"Loading images: {filenames}")
            self.add_images(filenames)

    def import_pdf(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Import PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )
        if filename:
            self.main_window.show_status_message(f"Importing PDF: {filename}")

            if self.project_manager.current_project is not None:
                self.project_manager.current_project.import_pdf(filename, progress_callback=self.main_window.update_progress_bar)

    def open_page(self, page_index: int) -> None:
        project = self.project_manager.current_project
        if project is None:
            return

        self.page_icon_view.open_page(page_index)
        self.page_editor_view.project_settings = project.settings
        self.page_editor_view.set_page(project.pages[page_index])

    def next_page(self) -> None:
        if self.project_manager.current_project is None:
            return

        current_page_index = self.page_icon_view.get_current_page_index()
        next_page_index = current_page_index + 1

        if next_page_index < len(self.project_manager.current_project.pages):
            self.open_page(next_page_index)

    def previous_page(self) -> None:
        if self.project_manager.current_project is None:
            return

        current_page_index = self.page_icon_view.get_current_page_index()
        previous_page_index = current_page_index - 1

        if previous_page_index >= 0:
            self.open_page(previous_page_index)

    def open_project(self) -> None:
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

        self.open_page(project.settings.get("current_page_index", 0))

        self.main_window.project_name_label.setText(f"Current project: {project.name}")
        self.page_editor_view.project_settings = project.settings
        self.page_icon_view.current_page_changed.connect(
            self.main_window.current_page_changed
        )
        self.page_editor_view.set_zoom(project.settings.get("zoom_level", 1.0))
        self.main_window.exporter_widget.set_project(project)

    def save_project(self) -> None:
        self.main_window.show_status_message("Saving project")

        if self.project_manager.current_project:
            if not self.project_manager.current_project.settings:
                return

            self.project_manager.current_project.settings.set(
                "current_page_index", self.page_icon_view.get_current_page_index()
            )
            self.project_manager.current_project.settings.set(
                "zoom_level", self.page_editor_view.current_zoom
            )

        self.project_manager.save_current_project(self.main_window.update_progress_bar)
        self.main_window.show_status_message("Project saved")

    def export_project(self) -> None:
        self.main_window.show_status_message("Exporting project")
        project = self.project_manager.current_project

        if not project:
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            exporter_dialog = ExporterPreviewDialog(
                project, self.main_window.application_settings, self.main_window
            )
            exporter_dialog.exec()

    def close_project(self) -> None:
        self.main_window.show_status_message("Closing project")
        self.project_manager.close_current_project()
        self.page_icon_view.clear()
        self.page_editor_view.clear()
        self.main_window.update()
        self.main_window.show_project_manager_dialog()

    def analyze_layout(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        self.main_window.show_status_message("Analyzing layout")
        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        current_page = controller.page
        current_page.analyze_page()

        for box in current_page.layout.ocr_boxes:
            controller.add_page_box_item_from_ocr_box(box)

    def recognize_boxes(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        self.main_window.show_status_message("Recognizing OCR boxes")
        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        current_page = controller.page
        current_page.recognize_ocr_boxes(
            progress_callback=self.main_window.update_progress_bar
        )
        self.ocr_editor()

    def analyze_layout_and_recognize(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        self.main_window.show_status_message("Analyzing layout and recognizing")
        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        current_page = controller.page
        current_page.analyze_page()
        current_page.recognize_ocr_boxes(
            progress_callback=self.main_window.update_progress_bar
        )

    def ocr_editor(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        controller.ocr_editor()

    def ocr_editor_project(self) -> None:
        self.main_window.ocr_editor_project()

    def set_header_footer_for_project(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        project = self.project_manager.current_project

        if not project:
            return

        for page in project.pages:
            page.set_header(controller.page.layout.header_y)
            page.set_footer(controller.page.layout.footer_y)

    def set_box_flow(self) -> None:
        view = self.main_window.page_editor_view

        if not view:
            return

        view.start_box_flow_selection()
