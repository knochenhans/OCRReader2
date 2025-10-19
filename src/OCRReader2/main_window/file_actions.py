from typing import List

from PySide6.QtWidgets import QFileDialog


class FileActions:
    def __init__(self, main_window, project_manager):
        self.main_window = main_window
        self.project_manager = project_manager

    def import_media_files(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Load images",
            "",
            "Images (*.png *.jpg *.jpeg *.pdf)",
        )
        if filenames:
            self.main_window.show_status_message(f"Loading images: {filenames}")
            self.project_manager.current_project.add_images(filenames)

    def import_pdf(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Import PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )
        if filename:
            self.main_window.show_status_message(f"Importing PDF: {filename}")
            self.project_manager.current_project.import_pdf(
                filename, progress_callback=self.main_window.update_progress_bar
            )

    def add_images(self, filenames: List[str]) -> None:
        if self.project_manager.current_project is not None:
            self.project_manager.current_project.add_images(filenames)
