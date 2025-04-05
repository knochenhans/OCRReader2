import os
import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtWidgets import QFileDialog
from platformdirs import user_data_dir

from ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog  # type: ignore
from project.project_manager import ProjectManager  # type: ignore
from settings.settings import Settings  # type: ignore


application_settings = Settings.from_dict(
    {
        "settings": {
            "is_maximized": True,
            "custom_shortcuts": {
                "Ctrl + 1": "section",
                "Alt + 1": "FLOWING_TEXT",
                "Alt + 2": "HEADING_TEXT",
                "Alt + 3": "PULLOUT_TEXT",
            },
            "tesseract_options": "preserve_interword_spaces=1",
            "thumbnail_size": 150,
            "merged_word_in_dict_color": 4278802740,
            "merged_word_not_in_dict_color": 4289010989,
            "editor_background_color": 4294966227,
            "max_font_size": 0,
            "min_font_size": 0,
            "round_font_size": 1,
            "scale_factor": 1.2,
            "box_flow_line_color": 4278190080,
            "box_type_tags": {
                "UNKNOWN": "",
                "FLOWING_TEXT": "p",
                "HEADING_TEXT": "h2",
                "PULLOUT_TEXT": "h3",
                "VERTICAL_TEXT": "p",
                "CAPTION_TEXT": "p",
                "EQUATION": "",
                "INLINE_EQUATION": "",
                "TABLE": "",
                "FLOWING_IMAGE": "",
                "HEADING_IMAGE": "",
                "PULLOUT_IMAGE": "",
                "HORZ_LINE": "",
                "VERT_LINE": "",
                "NOISE": "",
                "COUNT": "",
            },
            "confidence_color_threshold": 85,
            "box_flow_line_alpha": 128,
            "box_item_symbol_size": 16,
            "html_export_section_class": "section",
            "editor_text_color": 4278190080,
            "box_item_order_font_color": 4289010989,
            "box_item_symbol_font_color": 4289010989,
        }
    }
)


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
