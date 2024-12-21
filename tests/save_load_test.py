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


def test_save_load_boxes():
    box = OCRBox(x=100, y=750, width=230, height=50)
    box.order = 1
    box.confidence = 0.9
    box.class_ = "test"
    box.tag = "tag"
    box.type = BoxType.CAPTION_TEXT

    serialized = box.to_dict()

    with TemporaryDirectory() as temp_dir:
        file_path = f"{temp_dir}/box.json"

        with open(file_path, "w") as f:
            json.dump(serialized, f, indent=4)

        with open(file_path, "r") as f:
            loaded = OCRBox.from_dict(json.load(f))

        assert box.id == loaded.id
        assert box.order == loaded.order
        assert box.confidence == loaded.confidence
        assert box.class_ == loaded.class_
        assert box.tag == loaded.tag
        assert box.type == loaded.type
        assert box.x == loaded.x
        assert box.y == loaded.y
        assert box.width == loaded.width
        assert box.height == loaded.height
        assert box == loaded


def test_save_load_boxes2():
    page = Page(image_path, langs=langs)
    page.analyze()
    page.recognize_boxes()

    with TemporaryDirectory() as temp_dir:
        file_path = f"{temp_dir}/box.json"

        box = page.layout[2]

        with open(file_path, "w") as f:
            json.dump(box.to_dict(), f, indent=4)

        with open(file_path, "r") as f:
            loaded_data = json.load(f)

    box_type = loaded_data["type"]

    if box_type in BOX_TYPE_MAP:
        loaded = BOX_TYPE_MAP[box_type].from_dict(loaded_data)
    else:
        loaded = OCRBox.from_dict(loaded_data)

    TestCase().assertDictEqual(box.to_dict(), loaded.to_dict())
    assert box == loaded

def test_save_load_page():
    page = Page(image_path, langs=langs)
    page.analyze()
    page.recognize_boxes()

    with TemporaryDirectory() as temp_dir:
        file_path = f"{temp_dir}/page.json"

        with open(file_path, "w") as f:
            json.dump(page.to_dict(), f, indent=4)

        with open(file_path, "r") as f:
            loaded_data = json.load(f)

    loaded = Page.from_dict(loaded_data)

    assert page.image_path == loaded.image_path
    assert page.paper_size == loaded.paper_size
    assert page.ppi == loaded.ppi
    assert page.langs == loaded.langs
    assert page.layout.region == loaded.layout.region
    assert len(page.layout) == len(loaded.layout)

    for box, loaded_box in zip(page.layout, loaded.layout):
        assert box == loaded_box
