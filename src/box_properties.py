from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog, QMessageBox
import json
import sys

from main_window.box_properties_widget import BoxPropertiesWidget  # type: ignore
from project.project import Project  # type: ignore


def main():
    app = QApplication(sys.argv)

    # file_dialog = QFileDialog()
    # file_dialog.setNameFilter("JSON files (*.json)")
    # file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

    # if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
    #     file_path = file_dialog.selectedFiles()[0]
    # else:
    #     QMessageBox.warning(None, "Warning", "No file selected.")
    #     sys.exit()

    file_path = "/home/andre/.local/share/ocrreader/projects/b5650b08-80bb-491b-b52c-5c11f0e5cd33/b5650b08-80bb-491b-b52c-5c11f0e5cd33.json"

    with open(file_path, "r") as file:
        project_data = json.load(file)

    project = Project.from_dict(project_data)

    box = project.pages[0].layout.ocr_boxes[1]

    widget = BoxPropertiesWidget()
    widget.set_box([box])
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
