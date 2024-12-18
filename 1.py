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
    page.analyze_layout()

    # Uncomment the following lines if you want to debug the boxes
    # box_debugger = BoxDebugger()
    # box_debugger.show_boxes(page.image_path, page.layout.boxes)

    page.recognize_boxes()

    print("Finished processing image")


if __name__ == "__main__":
    main()
