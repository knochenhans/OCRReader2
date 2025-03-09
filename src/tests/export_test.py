import os
from tempfile import TemporaryDirectory
from src.exporter.exporter_preview import ExporterPreview
from src.page.box_type import BoxType
from src.project.project import ExporterType, Project
from src.exporter.exporter_epub import ExporterEPUB
from src.page.page import Page
from src.exporter.exporter_txt import ExporterTxt
from src.page.ocr_box import OCRBox
from settings import Settings # type: ignore
from iso639 import Lang  # type: ignore

project_settings = Settings.from_dict(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "",
    }
)
image_path = "data/1.jpeg"


def test_export_preview_merge_boxes1():
    boxes = [
        {
            "id": "1",
            "user_text": "Dies ist wirk-",
            "type": BoxType.FLOWING_TEXT,
            "flows_into_next": True,
        },
        {"id": "2", "user_text": "lich ein Test.", "type": BoxType.FLOWING_TEXT},
    ]

    exporter_preview = ExporterPreview("", "", Settings())
    merged = exporter_preview.merge_boxes(boxes, "de")

    assert len(merged) == 1
    assert merged[0]["user_text"] == "Dies ist wirklich ein Test."


def test_export_preview_merge_boxes2():
    boxes = [
        {
            "id": "1",
            "user_text": "Dies ist wirk-",
            "type": BoxType.FLOWING_TEXT,
            "flows_into_next": True,
        },
        {
            "id": "2",
            "user_text": "lich ein Test. Es ist tat- ",
            "type": BoxType.FLOWING_TEXT,
            "flows_into_next": True,
        },
        {"id": "3", "user_text": " sächlich ein Test.", "type": BoxType.FLOWING_TEXT},
    ]

    exporter_preview = ExporterPreview("", "", Settings())
    merged = exporter_preview.merge_boxes(boxes, "de")

    assert len(merged) == 1
    assert (
        merged[0]["user_text"]
        == "Dies ist wirklich ein Test. Es ist tatsächlich ein Test."
    )


def test_export_preview_merge_boxes3():
    boxes = [
        {
            "id": "1",
            "user_text": "Dies ist wirk-",
            "type": BoxType.FLOWING_TEXT,
            "flows_into_next": True,
        },
        {
            "id": "2",
            "user_text": "lich ein Test. Es ist tat- ",
            "type": BoxType.FLOWING_TEXT,
            "flows_into_next": True,
        },
        {"id": "3", "user_text": " sächlich ein Test.", "type": BoxType.FLOWING_TEXT},
        {"id": "4", "user_text": "ignore me", "type": BoxType.INLINE_EQUATION},
    ]

    exporter_preview = ExporterPreview("", "", Settings())
    merged = exporter_preview.merge_boxes(boxes, "de")

    assert len(merged) == 2
    assert (
        merged[0]["user_text"]
        == "Dies ist wirklich ein Test. Es ist tatsächlich ein Test."
    )
    assert merged[1]["user_text"] == "ignore me"


# def test_export_box():
#     page = Page(image_path)
#     page.set_settings(project_settings)
#     page.layout.add_ocr_box(OCRBox(x=90, y=747, width=380, height=380))
#     page.analyze_box(0)
#     page.recognize_boxes()

#     assert len(page.layout) == 2

#     with TemporaryDirectory() as temp_dir:
#         export_data = page.generate_page_export_data()

#         exporter = ExporterTxt(temp_dir, "test")
#         exporter.export_page(export_data)

#         with open(f"{temp_dir}/test.txt", "r") as f:
#             lines = f.readlines()

#         assert len(lines) == 2


# def test_export_project_epub():
#     with TemporaryDirectory() as temp_dir:
#         project_settings = ProjectSettings(
#             {
#                 "ppi": 300,
#                 "langs": ["deu"],
#                 "paper_size": "a4",
#                 "export_scaling_factor": 1.2,
#                 "export_path": temp_dir,
#             }
#         )

#         project = Project("Lines", "Lines")

#         project.set_settings(project_settings)
#         project.add_image(image_path)

#         for page in project.pages:
#             page.set_header(100)
#             page.set_footer(100)
#         project.analyze_pages()
#         page = project.pages[0]
#         page.recognize_boxes()

#         project.export(ExporterType.EPUB)

#         assert os.path.exists(f"{temp_dir}/Lines.epub")
