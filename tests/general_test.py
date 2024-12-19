from copy import deepcopy
from tesserocr import PyTessBaseAPI, RIL, PSM  # type: ignore
from src.box_debugger import BoxDebugger
from src.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR
from src.ocr_engine.ocr_box import OCRBox, TextBox
from src.ocr_engine.page import PageLayout, Page
from PIL import Image
from iso639 import Lang  # type: ignore

langs = [Lang("deu")]
ppi = 300
image_path = "data/1.jpeg"


def test_tesserocr():
    api = PyTessBaseAPI()
    api.Init(lang="deu+eng")
    api.SetImageFile(image_path)
    box = OCRBox(x=100, y=750, width=230, height=50)
    api.SetRectangle(box.x, box.y, box.width, box.height)
    assert api.GetUTF8Text().strip() == "Startschuß"


def test_general_tesserocr_engine():
    ocr_engine = OCREngineTesserOCR(langs)
    box = OCRBox(x=100, y=750, width=230, height=50)
    assert ocr_engine.recognize_box_text(image_path, ppi, box) == "Startschuß"


def test_general_tesserocr_engine2():
    ocr_engine = OCREngineTesserOCR(langs)
    box = OCRBox(x=100, y=70, width=200, height=45)
    assert ocr_engine.recognize_box_text(image_path, ppi, box) == "EDITORIAL"


def test_orientation_script():
    ocr_engine = OCREngineTesserOCR(langs)
    result = ocr_engine.detect_orientation_script(image_path, ppi)
    assert result["orientation"] == 0
    assert result["script"] == 1


def test_analyse_layout():
    ocr_engine = OCREngineTesserOCR(langs)
    result = ocr_engine.analyze_layout(image_path, ppi)
    assert len(result) == 24

    expected_result = OCRBox(x=104, y=74, width=193, height=29)
    box = deepcopy(result[2])
    assert box.x == expected_result.x
    assert box.y == expected_result.y
    assert box.width == expected_result.width
    assert box.height == expected_result.height

    if isinstance(box, TextBox):
        assert (
            ocr_engine.recognize_box_text(image_path, ppi, box).strip() == "EDITORIAL"
        )


def test_page_class():
    page = Page(image_path, langs=langs)
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
    page = Page(image_path, langs=langs)
    page.analyze_layout()

    box_0_id = page.layout[0].id

    page.recognize_boxes()

    assert len(page.layout) == 24
    assert page.layout[0].id == box_0_id


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
    page.analyze_layout()

    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(page.image_path, page.layout.boxes)

    assert len(page.layout) == 22
