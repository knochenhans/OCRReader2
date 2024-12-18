from copy import deepcopy
from tesserocr import PyTessBaseAPI, RIL, PSM  # type: ignore
from src.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from src.ocr_engine.ocr_box import OCRBox, TextBox
from src.ocr_engine.page import PageLayout, Page
from PIL import Image
from iso639 import Lang  # type: ignore

langs = [Lang("deu")]
ppi = 300


def test_tesserocr():
    api = PyTessBaseAPI()
    api.Init(lang="deu+eng")
    api.SetImageFile("data/1.jpeg")
    box = OCRBox(x=100, y=750, width=230, height=50)
    api.SetRectangle(box.x, box.y, box.width, box.height)
    assert api.GetUTF8Text().strip() == "Startschuß"


def test_general_tesserocr_engine():
    ocr_engine = OCREngineTesserOCR(langs)
    box = OCRBox(x=100, y=750, width=230, height=50)
    assert ocr_engine.recognize_box_text("data/1.jpeg", ppi, box) == "Startschuß"


def test_general_tesserocr_engine2():
    ocr_engine = OCREngineTesserOCR(langs)
    box = OCRBox(x=100, y=70, width=200, height=45)
    assert ocr_engine.recognize_box_text("data/1.jpeg", ppi, box) == "EDITORIAL"


def test_orientation_script():
    ocr_engine = OCREngineTesserOCR(langs)
    result = ocr_engine.detect_orientation_script("data/1.jpeg", ppi)
    assert result["orientation"] == 0
    assert result["script"] == 1


def test_analyse_layout():
    ocr_engine = OCREngineTesserOCR(langs)
    result = ocr_engine.analyze_layout("data/1.jpeg", ppi)
    assert len(result) == 24

    expected_result = OCRBox(x=104, y=74, width=193, height=29)
    box = deepcopy(result[2])
    assert box.x == expected_result.x
    assert box.y == expected_result.y
    assert box.width == expected_result.width
    assert box.height == expected_result.height

    if isinstance(box, TextBox):
        assert (
            ocr_engine.recognize_box_text("data/1.jpeg", ppi, box).strip()
            == "EDITORIAL"
        )


def test_page_class():
    page = Page("data/1.jpeg", langs=langs)
    page.analyze_layout()

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
    page = Page("data/1.jpeg", langs=langs)
    page.analyze_layout()
    page.recognize_boxes()

    assert len(page.layout) == 24
