from copy import deepcopy
import json
from tesserocr import PyTessBaseAPI, RIL, PSM  # type: ignore
from src.page.ocr_box import BOX_TYPE_MAP, BoxType
from src.box_debugger import BoxDebugger
from src.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from src.page.ocr_box import OCRBox, TextBox
from src.page.page import PageLayout, Page
from PIL import Image
from iso639 import Lang  # type: ignore
from unittest import TestCase
from tempfile import TemporaryDirectory

langs = [Lang("deu")]
ppi = 300
image_path = "data/1.jpeg"


def test_page_class():
    page = Page(image_path, langs=langs)
    page.analyze_page()

    assert len(page.layout) == 24


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

    layout.sort_boxes()

    assert len(layout) == 3
    assert layout[0].id == "A"
    assert layout[1].id == "B"
    assert layout[2].id == "C"

    layout.move_box(0, 2)

    assert len(layout) == 3

    assert layout[0].id == "B"
    assert layout[1].id == "C"
    assert layout[2].id == "A"

    layout.remove_box(1)

    assert len(layout) == 2

    assert layout[0].id == "B"
    assert layout[1].id == "A"


def test_page_ocr_results():
    page = Page(image_path, langs=langs)
    page.analyze_page()

    box_0_id = page.layout[0].id

    page.recognize_boxes()

    assert len(page.layout) == 24
    assert page.layout[0].id == box_0_id
    assert page.layout[0].order == 0
    assert page.layout[1].order == 1


def test_page_split_block():
    page = Page(image_path, langs=langs)
    page.layout.add_box(OCRBox(x=90, y=180, width=830, height=1120))
    page.analyze_box(0)

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(page.image_path, page.layout.boxes)

    assert len(page.layout) == 8


def test_page_header_footer():
    page = Page(image_path, langs=langs)
    page.layout.header_y = 200
    page.layout.footer_y = 200
    page.analyze_page()

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(page.image_path, page.layout.boxes)

    assert len(page.layout) == 22
