import sys
from PySide6.QtWidgets import QApplication, QDialog

from line_break_editor.line_break_dialog import LineBreakDialog
from page.ocr_box import TextBox  # type: ignore
from page.box_type import BoxType  # type: ignore


def main():
    app = QApplication(sys.argv)

    text_box = TextBox(0, 0, 0, 0, BoxType.FLOWING_TEXT)
    text_box.user_text = """Drei erstklassige Rennpfer-\nde hat Commodore mit den Amigas im Stall. Der Amiga 500 wird für frischen Wind in der gehobenen Heimcompu-\nterszene sorgen. Mit eingebau-\ntem Quatsch."""

    dialog = LineBreakDialog(text_box, "de")

    if dialog.exec() == QDialog.DialogCode.Accepted:
        text = dialog.get_text()
        print(f"Accepted: {text}")
    else:
        print("Cancelled")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
