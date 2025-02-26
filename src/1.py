import json
from tempfile import TemporaryDirectory
from project.project_settings import ProjectSettings  # type: ignore
from box_debugger import BoxDebugger  # type: ignore
from project.project_manager import ProjectManager  # type: ignore

import sys
from PIL import Image
from appdirs import user_data_dir, user_config_dir  # type: ignore
import os
from project.project import ExporterType  # type: ignore


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
    project_manager.new_project("Lines", "Lines")
    project = project_manager.get_project(-1)
    # project = project_manager.get_project_by_uuid(
    #     "8fb8054a-563a-4ad9-b153-93d9e4115f6e"
    # )

    if project is not None:
        project.set_settings(project_settings)
        # project.import_pdf("data/Amiga Magazin 1987-06..07.pdf", 0, 10)
        project.add_image("src/data/3.jpeg")

        for page in project.pages:
            page.set_header(100)
            page.set_footer(100)
        project.analyze_pages()
        page = project.pages[0]
        page.recognize_ocr_boxes(2)
        # project.recognize_page_boxes()
        # project_manager.save_project(0)

        box_debugger = BoxDebugger()
        box_debugger.show_boxes(project.pages[0].image_path, project.pages[0].layout.ocr_boxes)

        # project.export(ExporterType.EPUB)


if __name__ == "__main__":
    main()
