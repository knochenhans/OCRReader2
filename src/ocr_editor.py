import json
import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtWidgets import QFileDialog, QMessageBox

from line_break_editor.ocr_edit_dialog import OCREditDialog  # type: ignore
from page.ocr_box import TextBox  # type: ignore
from page.box_type import BoxType  # type: ignore
from project.project import Project  # type: ignore
from page.page import Page  # type: ignore


def main():
    app = QApplication(sys.argv)

    file_dialog = QFileDialog()
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

    if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
        file_path = file_dialog.selectedFiles()[0]
    else:
        QMessageBox.warning(None, "Warning", "No file selected.")
        sys.exit()

    with open(file_path, "r") as file:
        project_data = json.load(file)

    project = Project.from_dict(project_data)

    dialog = OCREditDialog(project.pages, "de")

    if dialog.exec() == QDialog.DialogCode.Accepted:
        pass
        # if text_box.ocr_results:
        #     print(text_box.user_text)

    else:
        print("Cancelled")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
