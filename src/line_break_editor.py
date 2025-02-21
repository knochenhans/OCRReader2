import json
import sys
from PySide6.QtWidgets import QApplication, QDialog

from src.line_break_editor.ocr_edit_dialog import OCREditDialog
from page.ocr_box import TextBox  # type: ignore
from page.box_type import BoxType  # type: ignore


def main():
    app = QApplication(sys.argv)

    # text_box = TextBox(0, 0, 0, 0, BoxType.FLOWING_TEXT)
    # text_box.user_text = """Drei erstklassige Rennpfer-\nde hat Commodore mit den Amigas\n im Stall.\nDer \nAmiga 500 wird für frischen Wind in der gehobenen Heimcompu-\nterszene sorgen. Mit eingebau-\ntem Quatsch."""

    json_file = "src/line_break_editor/test_block.json"

    # Load json file as dict
    with open(json_file, "r") as file:
        data = json.load(file)

    text_box = TextBox.from_dict(data)

    dialog = OCREditDialog(text_box, "de")

    if dialog.exec() == QDialog.DialogCode.Accepted:
        if text_box.ocr_results:
            for paragraph in text_box.ocr_results.paragraphs:
                print(paragraph.user_text)

    else:
        print("Cancelled")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
