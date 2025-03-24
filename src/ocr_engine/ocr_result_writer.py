from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument
from ocr_engine.ocr_result import OCRResultBlock, OCRResultSymbol, OCRResultWord  # type: ignore
from settings import Settings  # type: ignore
import aspell  # type: ignore
from bs4 import BeautifulSoup
from loguru import logger


class TextPartType(Enum):
    TEXT = 0
    HYPHENATED_WORD = 1


@dataclass
class TextPart:
    part_type: TextPartType
    text: str
    word_first_part_with_hyphen: str
    word_second_part: str


class OCRResultWriter:
    def __init__(
        self,
        application_settings: Settings,
        lang: str,
        blacklist: Optional[List[str]] = None,
    ) -> None:
        self.application_settings = application_settings
        self.text_parts: List[TextPart] = []
        self.buffer_word: bool = False
        self.word_first_part_with_hyphen = ""
        self.word_first_part_hyphenized = ""

        self.lang = lang
        self.blacklist = blacklist

        self.spell = aspell.Speller("lang", self.lang)

    def _check_hyphenated_word(self, first_part: str, second_part: str) -> bool:
        # Strip the HTML tags using BeautifulSoup
        first_part_stripped = (
            BeautifulSoup(first_part, "html.parser").get_text().strip()
        )
        second_part_stripped = (
            BeautifulSoup(second_part, "html.parser").get_text().strip()
        )

        if self.blacklist is not None:
            # Check if the second part is in the blacklist
            if second_part_stripped.lower() in self.blacklist:
                return False

        # Check if the second part starts with a capital letter
        if second_part_stripped[0].isupper():
            return False

        # TODO: Disable spell checking for now
        # return self._check_spelling(first_part_stripped + second_part_stripped)
        return True

    def _check_spelling(self, word: str) -> bool:
        # Remove non-alphanumeric characters for checking
        word = "".join(e for e in word if e.isalnum())
        return self.spell.check(word)

    def _set_confidence_color_background(
        self,
        format: QTextCharFormat,
        element: OCRResultWord | OCRResultSymbol,
        confidence_color_threshold: int,
    ) -> None:
        if element.confidence < confidence_color_threshold:
            format.setBackground(
                QColor(*element.get_confidence_color(confidence_color_threshold))
            )

    def to_qdocument(self, ocr_result_blocks: list[OCRResultBlock]) -> QTextDocument:
        document = QTextDocument()
        cursor = QTextCursor(document)

        symbol_str = ""
        word_str = ""
        is_hyphenated_word = False
        word_position = 0
        hyphenated_word_start_position = 0

        confidence_color_threshold = self.application_settings.get(
            "confidence_color_threshold", 50
        )

        merged_word_not_in_dict_color = self.application_settings.get(
            "merged_word_not_in_dict_color", QColor(0, 255, 0, 255).rgba()
        )
        # merged_word_not_in_dict_color = self.application_settings.get(
        #     "merged_word_not_in_dict_color", QColor(255, 0, 0, 255).rgba()
        # )

        text_color_format = QTextCharFormat()

        for block_index, block in enumerate(ocr_result_blocks):
            for paragraph_index, paragraph in enumerate(block.paragraphs):
                for line_index, line in enumerate(paragraph.lines):
                    for word_index, word in enumerate(line.words):
                        word_str = word.get_text()

                        word_position = cursor.position()

                        # First word of a line
                        if word_index == 0:
                            if is_hyphenated_word:
                                if self.blacklist is not None:
                                    if word_str in self.blacklist:
                                        cursor.insertText("- ")

                                if word_str[0].isupper():
                                    cursor.insertText("-")
                            elif symbol_str.strip() != "" and not (
                                line_index == 0 and word_index == 0
                            ):
                                cursor.insertText(" ", text_color_format)
                        else:
                            cursor.insertText(" ", text_color_format)

                        word_format = QTextCharFormat()
                        self._set_confidence_color_background(
                            word_format, word, confidence_color_threshold
                        )

                        for symbol_index, symbol in enumerate(word.symbols):
                            symbol_str = symbol.get_text()

                            symbol_format = QTextCharFormat(word_format)
                            self._set_confidence_color_background(
                                symbol_format, symbol, confidence_color_threshold
                            )

                            if (
                                word_index == len(line.words) - 1
                                and symbol_index == len(word.symbols) - 1
                                and symbol_str == "-"
                            ):
                                # Last word of a line and last symbol is a hyphen
                                is_hyphenated_word = True

                                hyphenated_word_start_position = word_position

                                if block_index < len(ocr_result_blocks):
                                    break

                            cursor.insertText(symbol_str, symbol_format)

                        if word_index == 0 and not word_index == len(line.words) - 1:
                            if is_hyphenated_word:
                                current_position = cursor.position()
                                text_color_format.setForeground(
                                    QColor(merged_word_not_in_dict_color)
                                )
                                cursor.setPosition(hyphenated_word_start_position)
                                cursor.setPosition(
                                    current_position, QTextCursor.MoveMode.KeepAnchor
                                )
                                cursor.mergeCharFormat(text_color_format)
                                cursor.movePosition(QTextCursor.MoveOperation.End)

                            is_hyphenated_word = False
                        text_color_format = QTextCharFormat()

                if paragraph_index < len(block.paragraphs) - 1:
                    cursor.insertText("\n")
            if block_index < len(ocr_result_blocks) - 1:
                cursor.insertText("\n")

        # Readd hyphen if it is the last character
        if is_hyphenated_word:
            cursor.insertText("-")

        return document
