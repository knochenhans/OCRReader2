import json
from tempfile import TemporaryDirectory
from src.exporter.exporter_odt import ExporterODT
from src.exporter.exporter_html import ExporterHTML
from src.page.ocr_box import BOX_TYPE_MAP, OCRBox
from src.box_debugger import BoxDebugger
from src.page.page import Page
from iso639 import Lang
import sys
from PIL import Image


def main():
    images = ["data/1.jpeg"]
    langs = [Lang("deu")]

    # Load and display the image using PIL
    # image = Image.open(images[0])
    # image.show()

    # Process the image with OCR
    page = Page(images[0], langs=langs)
    page.layout.add_box(OCRBox(x=90, y=180, width=1600, height=950))
    # page.align_box(0)
    page.analyze_box(0)
    page.recognize_boxes()
    # page.analyze()

    box_debugger = BoxDebugger()
    box_debugger.show_boxes(page.image_path, page.layout.boxes)

    # print("Finished processing image")

    export_data = page.generate_export_data()

    # exporter = ExporterTxt("/tmp/ocrexport/export.txt")
    # exporter = ExporterODT("/tmp/ocrexport/export.odt")
    exporter = ExporterHTML("/tmp/ocrexport/export.html")
    exporter.scaling_factor = 1.2
    exporter.export(export_data)

    # page = Page(images[0], langs=langs)
    # page.analyze()
    # page.recognize_boxes()

    # with TemporaryDirectory() as temp_dir:
    #     file_path = f"{temp_dir}/box.json"

    #     box = page.layout[2]

    #     with open(file_path, "w") as f:
    #         json.dump(box.to_dict(), f, indent=4)

    #     with open(file_path, "r") as f:
    #         loaded_data = json.load(f)

    #         box_type = loaded_data["type"]

    #         if box_type in BOX_TYPE_MAP:
    #             loaded = BOX_TYPE_MAP[box_type].from_dict(loaded_data)
    #         else:
    #             loaded = OCRBox.from_dict(loaded_data)


if __name__ == "__main__":
    main()
