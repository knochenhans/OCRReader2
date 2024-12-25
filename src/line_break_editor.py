import sys
from PySide6.QtWidgets import QApplication

from line_break_editor.line_break_dialog import LineBreakDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = LineBreakDialog()
    dialog.show()
    sys.exit(app.exec())
