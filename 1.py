from src.ocr_engine.ocr_box import OCRBox
from src.box_debugger import BoxDebugger
from src.ocr_engine.page import Page
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
    page.layout.add_box(OCRBox(x=90, y=180, width=730, height=930))
    page.analyze_box(0)
    # page.analyze_layout()

    box_debugger = BoxDebugger()
    box_debugger.show_boxes(page.image_path, page.layout.boxes)

    print("Finished processing image")


if __name__ == "__main__":
    main()
