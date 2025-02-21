from copy import deepcopy
from enum import Enum, auto
import aspell  # type: ignore
import string
import re
from typing import List, Tuple, Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QApplication
from PySide6.QtGui import QTextCursor, QTextCharFormat, QColor

from page.ocr_box import TextBox  # type: ignore
from ocr_engine.ocr_result import OCRResultParagraph, OCRResultWord  # type: ignore


class PartType(Enum):
    TEXT = auto()
    WORD = auto()


PartInfo = Tuple[
    PartType, str, str, bool, bool, OCRResultWord, OCRResultWord
]  # type, unmerged text, merged text, is in dictionary, use merged


class OCREditController(QObject):
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

    def remove_line_breaks(
        self, ocr_result_paragraph: OCRResultParagraph
    ) -> List[PartInfo]:
        parts: List[PartInfo] = []

        merge = False

        for line in ocr_result_paragraph.lines:
            for word in line.words:
                if word.text.endswith("-"):
                    merge = True
                    parts.append((PartType.WORD, word.text, "", False, False, word, word))
                elif merge:
                    merge = False

                    word_last = parts[-1][5]
                    unmerged_word = word_last.text + word.text
                    merged_word = word_last.text[:-1] + word.text
                    word_unmerged_deepcopy = deepcopy(parts[-1][5])
                    word_unmerged_deepcopy.text = unmerged_word
                    word_merged_deepcopy = deepcopy(parts[-1][5])
                    word_merged_deepcopy.text = merged_word

                    if isinstance(word_unmerged_deepcopy, OCRResultWord):
                        parts[-1] = (
                            PartType.WORD,
                            merged_word,
                            word_unmerged_deepcopy.get_confidence_html(),
                            False,
                            False,
                            word_unmerged_deepcopy,
                            word_merged_deepcopy,
                        )
                else:
                    parts.append((PartType.TEXT, word.text, "", False, False, word, word))

        return parts

    def check_merged_word(self, part_info: PartInfo) -> PartInfo:
        if part_info[0] == PartType.WORD:
            merged_word = self.merge_word(part_info[1])
            is_correct = self.spell.check(merged_word)
            return (
                part_info[0],
                part_info[1],
                merged_word,
                is_correct,
                is_correct,
                part_info[5],
                part_info[6],
            )
        return part_info
