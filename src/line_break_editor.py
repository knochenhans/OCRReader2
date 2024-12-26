import sys
from PySide6.QtWidgets import QApplication, QDialog

from line_break_editor.line_break_dialog import LineBreakDialog


def main():
    app = QApplication(sys.argv)
    dialog = LineBreakDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        text = dialog.get_text()
        print(f"Accepted: {text}")
    else:
        print("Cancelled")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
