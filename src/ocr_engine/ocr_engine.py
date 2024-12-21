from typing import List, Optional
import cv2
from iso639 import Lang  # type: ignore
from src.ocr_engine.ocr_box import OCRBox
from PySide6.QtCore import QObject


class OCREngine(QObject):
    def __init__(self, langs: Optional[List], ppi: int = 300) -> None:
        self.langs = langs
        self.settings = {
            "ppi": ppi,
            "padding": 10,
        }

    def recognize_box_text(self, image_path: str, box: OCRBox) -> str:
        return ""
