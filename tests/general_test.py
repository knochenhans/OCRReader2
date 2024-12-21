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
