from typing import List

from PySide6 import QtWidgets


class OCRReader2(QtWidgets.QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
