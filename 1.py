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
    langs = [Lang("deu")]

    data_dir = user_data_dir("pyocr", "pyocr")

    # # make sure the data directory exists

    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)

    # project = Project("Test Project", "A test project")
    # project.langs = langs
    # project.output_path = "/tmp/ocrexport"
    # project.project_root_path = data_dir
    # project.add_image("data/1.jpeg")
    # # project.add_image("data/2.jpeg")
    # # project.add_image("data/3.jpeg")
    # project.analyze_pages()
    # project.recognize_page_boxes()
    # project.export()

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.boxes)

    project_manager = ProjectManager(data_dir)
    # project_manager.new_project("Test Project", "A test project")
    project = project_manager.get_project(0)
    # project.set_settings(project_settings)
    # project.add_image("data/1.jpeg")
    # project.analyze_pages()
    # project.recognize_page_boxes()
    # project_manager.save_project(0)

    box_debugger = BoxDebugger()
    box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.boxes)


if __name__ == "__main__":
    main()
