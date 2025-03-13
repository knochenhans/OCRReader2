import json
import os
import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtWidgets import QFileDialog, QMessageBox
from platformdirs import user_data_dir

from ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog  # type: ignore
from page.ocr_box import TextBox  # type: ignore
from page.box_type import BoxType  # type: ignore
from project.project import Project  # type: ignore
from project.project_manager import ProjectManager  # type: ignore
from page.page import Page  # type: ignore
from ocr_processor import OCRProcessor
from settings import Settings  # type: ignore


def main():
    app = QApplication(sys.argv)

    file_dialog = QFileDialog()
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

    # if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
    #     file_path = file_dialog.selectedFiles()[0]
    # else:
    #     QMessageBox.warning(None, "Warning", "No file selected.")
    #     sys.exit()

    # with open(file_path, "r") as file:
    #     project_data = json.load(file)

    # project = Project.from_dict(project_data)

    project_manager = ProjectManager(
        os.path.join(user_data_dir("ocrreader", "ocrreader"), "projects")
    )

    project = project_manager.load_project_by_index(0)

    application_settings = Settings()
    dialog = OCREditorDialog(project.pages, "de", application_settings)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        pass
        # if text_box.ocr_results:
        #     print(text_box.user_text)

    else:
        print("Cancelled")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
