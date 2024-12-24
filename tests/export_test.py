import os
from tempfile import TemporaryDirectory
from src.project import ExporterType, Project
from src.exporter.exporter_epub import ExporterEPUB
from src.page.page import Page
from src.exporter.exporter_txt import ExporterTxt
from src.page.ocr_box import OCRBox
from project_settings import ProjectSettings
from iso639 import Lang  # type: ignore

project_settings = ProjectSettings(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "",
    }
)
image_path = "data/1.jpeg"


def test_export_box():
    page = Page(image_path)
    page.set_settings(project_settings)
    page.layout.add_box(OCRBox(x=90, y=747, width=380, height=380))
    page.analyze_box(0)
    page.recognize_boxes()

    assert len(page.layout) == 2

    with TemporaryDirectory() as temp_dir:
        export_data = page.generate_page_export_data()

        exporter = ExporterTxt(temp_dir, "test")
        exporter.export_page(export_data)

        with open(f"{temp_dir}/test.txt", "r") as f:
            lines = f.readlines()

        assert len(lines) == 2


def test_export_project_epub():
    with TemporaryDirectory() as temp_dir:
        project_settings = ProjectSettings(
            {
                "ppi": 300,
                "langs": ["deu"],
                "paper_size": "a4",
                "export_scaling_factor": 1.2,
                "export_path": temp_dir,
            }
        )

        project = Project("Lines", "Lines")

        project.set_settings(project_settings)
        project.add_image(image_path)

        for page in project.pages:
            page.set_header(100)
            page.set_footer(100)
        project.analyze_pages()
        page = project.pages[0]
        page.recognize_boxes()

        project.export(ExporterType.EPUB)

        assert os.path.exists(f"{temp_dir}/Lines.epub")
