from settings.settings import Settings
from src.ocr_processor import OCRProcessor
from src.page.ocr_box import OCRBox
from src.page.page import Page

project_settings = Settings.from_dict(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "",
        "tesseract_data_path": "/usr/share/tessdata",
    }
)
image_path = "data/1.jpeg"


def test_merge_boxes1():
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    box1 = OCRBox(x=0, y=0, width=50, height=50)
    box2 = OCRBox(x=0, y=50, width=50, height=50)

    page.layout.add_ocr_box(box1)
    page.layout.add_ocr_box(box2)

    page.merge_ocr_box_with_ocr_box(0, 1)

    assert len(page.layout) == 1
    assert page.layout[0].x == 0
    assert page.layout[0].y == 0
    assert page.layout[0].width == 50
    assert page.layout[0].height == 100


def test_merge_boxes2():
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    box1 = OCRBox(x=0, y=0, width=50, height=50)
    box2 = OCRBox(x=0, y=100, width=50, height=50)

    page.layout.add_ocr_box(box1)
    page.layout.add_ocr_box(box2)

    page.merge_ocr_box_with_ocr_box(0, 1)

    assert len(page.layout) == 1
    assert page.layout[0].x == 0
    assert page.layout[0].y == 0
    assert page.layout[0].width == 50
    assert page.layout[0].height == 150


def test_merge_boxes_overlapping1():
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    box1 = OCRBox(x=0, y=0, width=50, height=50)
    box2 = OCRBox(x=0, y=25, width=50, height=50)

    page.layout.add_ocr_box(box1)
    page.layout.add_ocr_box(box2)

    page.merge_ocr_box_with_ocr_box(0, 1)

    assert len(page.layout) == 1
    assert page.layout[0].x == 0
    assert page.layout[0].y == 0
    assert page.layout[0].width == 50
    assert page.layout[0].height == 75


def test_merge_boxes_overlapping2():
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    box1 = OCRBox(x=0, y=0, width=50, height=50)
    box2 = OCRBox(x=0, y=25, width=50, height=50)
    box3 = OCRBox(x=0, y=75, width=50, height=50)

    page.layout.add_ocr_box(box1)
    page.layout.add_ocr_box(box2)
    page.layout.add_ocr_box(box3)

    page.merge_ocr_box_with_ocr_box(0, 1)
    page.merge_ocr_box_with_ocr_box(0, 1)

    assert len(page.layout) == 1
    assert page.layout[0].x == 0
    assert page.layout[0].y == 0
    assert page.layout[0].width == 50
    assert page.layout[0].height == 125
