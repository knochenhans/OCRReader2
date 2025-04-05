import os
import sys
from PySide6.QtWidgets import QApplication
from platformdirs import user_data_dir

from page_editor.page_editor_view import PageEditorView
from project.project_manager import ProjectManager
from settings.settings import Settings
from ocr_processor import OCRProcessor  # type: ignore

# project_settings = Settings.from_dict(
#     {
#         "ppi": 300,
#         "langs": ["deu"],
#         "paper_size": "a4",
#         "export_scaling_factor": 1.2,
#         "export_path": "/tmp/ocrexport",
#     }
# )


def main():
    user_data_dir_ = user_data_dir("ocrreader", "ocrreader")

    # def print_state():
    #     with open("/tmp/status1.txt", "w") as f:
    #         f.write(str(page.layout.ocr_boxes))

    app = QApplication(sys.argv)

    data_dir = user_data_dir("ocrreader", "ocrreader")

    project_manager = ProjectManager(os.path.join(data_dir, "projects"))
    # project_manager.new_project("Test", "Test")
    project = project_manager.load_project_by_index(0)
    # project.set_settings(project_settings)
    # project.add_image("src/data/3.jpeg")

    page_number = 10

    page = project.pages[page_number]
    project_manager.get_ocr_results_for_page(project, page_number)
    page.ocr_processor = OCRProcessor(project.settings)
    # page.layout.ocr_boxes = [OCRBox(x=10, y=10, width=100, height=100)]

    # page.set_header(100)
    # page.set_footer(100)
    # project.analyze_pages()
    # page.recognize_boxes()

    # print_state()

    application_settings = Settings("application_settings", user_data_dir_)
    application_settings.load()

    dialog = PageEditorView(application_settings=application_settings)
    dialog.set_page(page)

    dialog.custom_shortcuts = application_settings.settings.get("custom_shortcuts", {})

    dialog.closeEvent = lambda event: project_manager.save_current_project()

    dialog.show()

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.boxes)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
