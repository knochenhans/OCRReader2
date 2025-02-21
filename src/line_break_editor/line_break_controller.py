from enum import Enum, auto
import aspell  # type: ignore
from page.ocr_box import TextBox  # type: ignore
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QApplication
from PySide6.QtGui import QTextCursor, QTextCharFormat, QColor
import string
import re
from typing import List, Tuple, Optional


class PartType(Enum):
    TEXT = auto()
    WORD = auto()


PartInfo = Tuple[
    PartType, str, str, bool, bool
]  # type, unmerged text, merged text, is in dictionary, use merged


class LineBreakController(QObject):
    box_text_changed = Signal(str)

    def __init__(self, ocr_text_box: TextBox, lang: str) -> None:
        super().__init__()
        self.ocr_box = ocr_text_box
        self.lang = lang

        self.spell = aspell.Speller("lang", self.lang)

    def get_box_text(self) -> str:
        text = ""

        if self.ocr_box.user_text:
            text = self.ocr_box.user_text
        else:
            if self.ocr_box.ocr_results:
                text = self.ocr_box.ocr_results.get_text()
        return text

    def set_box_text(self, text: str) -> None:
        self.ocr_box.user_text = text
        self.box_text_changed.emit(text)

    def merge_word(self, word: str) -> str:
        return word.replace("-\n", "")

    def remove_line_breaks(self, text: str) -> List[PartInfo]:
        parts: List[PartInfo] = []

        while True:
            match = re.search(r"^(.*?)(\w+-\n\w+)(.*?)$", flags=re.DOTALL, string=text)
            if match:
                parts.append(
                    (PartType.TEXT, match.group(1).replace("\n", " "), "", False, False)
                )
                parts.append(
                    (
                        PartType.WORD,
                        match.group(2),
                        self.merge_word(match.group(2)),
                        False,
                        False,
                    )
                )
                text = match.group(3)
            else:
                parts.append((PartType.TEXT, text.replace("\n", " "), "", False, False))
                break

        return parts

    def check_merged_word(self, part_info: PartInfo) -> PartInfo:
        if part_info[0] == PartType.WORD:
            merged_word = self.merge_word(part_info[1])
            is_correct = self.spell.check(merged_word)
            return (part_info[0], part_info[1], merged_word, is_correct, is_correct)
        return part_info
