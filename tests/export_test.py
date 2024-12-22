from copy import deepcopy
import json
from src.exporter.exporter_html import ExporterHTML
from src.page.ocr_box import BOX_TYPE_MAP, BoxType
from src.page.ocr_box import OCRBox
from src.page.page import Page
from PIL import Image
from iso639 import Lang  # type: ignore
from unittest import TestCase
from tempfile import TemporaryDirectory

langs = [Lang("deu")]
ppi = 300
image_path = "data/1.jpeg"


def test_export_box():
    page = Page(image_path, langs=langs)
    page.layout.add_box(OCRBox(x=90, y=747, width=380, height=380))
    page.analyze_box(0)
    page.recognize_boxes()

    assert len(page.layout) == 2

    with TemporaryDirectory() as temp_dir:
        export_data = page.generate_export_data()

        exporter = ExporterHTML(temp_dir, "export.html")
        exporter.export(export_data)

        with open(f"{temp_dir}/export.html", "r") as f:
            html = f.read()

            # assert "<!DOCTYPE html>" in html
            # assert "<html>" in html
            # assert "<head>" in html
            # assert "<body>" in html
            # assert "<h1>OCR Export</h1>" in html
            # assert "<h2>Page</h2>" in html
            # assert f'<img src="{image_path}" />' in html
            # assert "<h2>Boxes</h2>" in html
            # assert '<div class="box" style="left: 90px; top: 747px; width: 380px; height: 380px;">' in html
            # assert "</body>" in html
            # assert "</html>" in html
            # assert "</head>" in html



