import sys
from PySide6.QtWidgets import QApplication, QDialog
from platformdirs import user_data_dir

from page_editor.page_editor_view import PageEditorView
from project.project_manager import ProjectManager
from project.project_settings import ProjectSettings

project_settings = ProjectSettings(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "/tmp/ocrexport",
    }
)

def main():
    app = QApplication(sys.argv)

    data_dir = user_data_dir("ocrreader", "ocrreader")

    project_manager = ProjectManager(data_dir)
    project_manager.new_project("Test", "Test")
    project = project_manager.get_project(-1)
    project.set_settings(project_settings)
    project.add_image("src/data/3.jpeg")
    page = project.pages[0]
    page.set_header(100)
    page.set_footer(100)
    project.analyze_pages()
    # page.recognize_boxes()

    dialog = PageEditorView(page)

    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
