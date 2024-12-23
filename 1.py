import json
from tempfile import TemporaryDirectory
from project_settings import ProjectSettings
from src.box_debugger import BoxDebugger
from project_manager import ProjectManager

from iso639 import Lang
import sys
from PIL import Image
from appdirs import user_data_dir, user_config_dir
import os
from src.project import ExporterType


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
    data_dir = user_data_dir("pyocr", "pyocr")

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.boxes)

    project_manager = ProjectManager(data_dir)
    project_manager.new_project("Test Project", "A test project")
    project = project_manager.get_project(0)
    project.set_settings(project_settings)
    project.add_image("data/1.jpeg")
    page = project.pages[0]
    page.set_header(100)
    page.set_footer(100)
    project.analyze_pages()
    project.recognize_page_boxes()
    project_manager.save_project(0)

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.boxes)

    project.export(ExporterType.EPUB)


if __name__ == "__main__":
    main()
