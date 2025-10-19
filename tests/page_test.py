import pytest

from settings.settings import Settings
# from src.box_debugger import BoxDebugger
from src.ocr_processor import OCRProcessor
from src.page.ocr_box import OCRBox
from src.page.page import Page, PageLayout


@pytest.fixture
def project_settings():
    return Settings.from_dict(
        {
            "ppi": 300,
            "langs": ["deu"],
            "paper_size": "a4",
            "export_scaling_factor": 1.2,
            "export_path": "",
            "tesseract_data_path": "/usr/share/tessdata",
            "layout_analyzer": "tesserocr",
        }
    )


@pytest.fixture
def image_path():
    return "data/1.jpeg"


@pytest.fixture
def page(project_settings, image_path):
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    return page


def test_page_class(page, project_settings):
    page.analyze_page(project_settings, filter_by_box_types=False, filter_by_size=False)

    assert len(page.layout) == 18


def test_page_layout_box_order():
    layout = PageLayout(
        [
            OCRBox(x=0, y=0, width=100, height=100),
            OCRBox(x=0, y=0, width=100, height=100),
            OCRBox(x=0, y=0, width=100, height=100),
        ]
    )

    # Set IDs for testing
    layout[0].id = "A"
    layout[1].id = "B"
    layout[2].id = "C"

    layout.sort_ocr_boxes_by_order()

    assert len(layout) == 3
    assert layout[0].id == "A"
    assert layout[1].id == "B"
    assert layout[2].id == "C"

    layout.change_box_index(0, 2)

    assert len(layout) == 3
    assert layout[0].id == "B"
    assert layout[1].id == "C"
    assert layout[2].id == "A"

    layout.remove_ocr_box(1)

    assert len(layout) == 2
    assert layout[0].id == "B"
    assert layout[1].id == "A"


def test_page_ocr_results(page, project_settings):
    page.analyze_page(project_settings)
    box_0_id = page.layout[0].id
    page.recognize_ocr_boxes()

    assert len(page.layout) == 18
    assert page.layout[0].id == box_0_id
    assert page.layout[0].order == 0
    assert page.layout[1].order == 1


def test_page_split_block(page):
    page.layout.add_ocr_box(OCRBox(x=90, y=180, width=830, height=1120))
    # page.analyze_ocr_box(0)

    assert len(page.layout) == 1

    box_id = page.layout[0].id

    page.layout.split_y_ocr_box(box_id, 200)

    assert len(page.layout) == 2

    assert page.layout[0].id == box_id
    assert page.layout[0].y == 180
    assert page.layout[0].height == 20
    assert page.layout[1].y == 200
    assert page.layout[1].height == 1100


def test_page_header_footer(page, project_settings):
    page.layout.header_y = 200
    page.layout.footer_y = 2310 - 100
    page.analyze_page(project_settings)

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(page.image_path, page.layout)

    assert len(page.layout) == 13


def test_reorder_blocks(page, project_settings):
    page.analyze_page(project_settings)

    assert len(page.layout) == 18

    box_0_id = page.layout[0].id
    box_1_id = page.layout[1].id
    box_2_id = page.layout[2].id
    page.layout.change_box_index(0, 2)

    assert len(page.layout) == 18
    assert page.layout[0].id == box_1_id
    assert page.layout[1].id == box_2_id
    assert page.layout[2].id == box_0_id


def test_insert_block(page, project_settings):
    page.analyze_page(project_settings)

    assert len(page.layout) == 18

    box_0_id = page.layout[0].id
    box_1_id = page.layout[1].id
    box_2_id = page.layout[2].id
    new_box = OCRBox(x=0, y=0, width=100, height=100)
    page.layout.add_ocr_box(new_box, 1)

    assert len(page.layout) == 19
    assert page.layout[0].id == box_0_id
    assert page.layout[0].order == 0
    assert page.layout[1].id != box_1_id
    assert page.layout[1].id == new_box.id
    assert page.layout[1].order == 1
    assert page.layout[2].id == box_1_id
    assert page.layout[2].order == 2
    assert page.layout[3].id == box_2_id
    assert page.layout[3].order == 3


def test_sort_ocr_boxes_by_order():
    layout = PageLayout(
        [
            OCRBox(x=0, y=0, width=100, height=100, order=2),
            OCRBox(x=0, y=0, width=100, height=100, order=1),
            OCRBox(x=0, y=0, width=100, height=100, order=0),
        ]
    )

    id1 = layout[0].id
    id2 = layout[1].id
    id3 = layout[2].id

    layout.sort_ocr_boxes_by_order()

    assert layout[0].order == 0
    assert layout[1].order == 1
    assert layout[2].order == 2
    assert layout[0].id == id3
    assert layout[1].id == id2
    assert layout[2].id == id1


def test_update_order():
    layout = PageLayout(
        [
            OCRBox(x=0, y=0, width=100, height=100, order=2),
            OCRBox(x=0, y=0, width=100, height=100, order=1),
            OCRBox(x=0, y=0, width=100, height=100, order=0),
        ]
    )

    layout.update_order()

    assert layout[0].order == 0
    assert layout[1].order == 1
    assert layout[2].order == 2
