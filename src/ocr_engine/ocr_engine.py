from typing import List, Optional
import cv2
from iso639 import Lang  # type: ignore
from page.ocr_box import OCRBox # type: ignore
from PySide6.QtCore import QObject


class OCREngine(QObject):
    def __init__(self, langs: Optional[List], ppi: int = 300) -> None:
        self.langs = langs
        self.settings = {
            "ppi": ppi,
            "padding": 10,
        }

    def recognize_box_text(self, image_path: str, ppi: int, box: OCRBox) -> str:
        return ""
