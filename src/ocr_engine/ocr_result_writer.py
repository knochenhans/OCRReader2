from dataclasses import dataclass
from enum import Enum
from typing import List
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument
from ocr_engine.ocr_result import OCRResultBlock, OCRResultSymbol, OCRResultWord  # type: ignore
from settings import Settings  # type: ignore


class TextPartType(Enum):
    TEXT = 0
    HYPHENATED_WORD = 1


@dataclass
class TextPart:
    part_type: TextPartType
    text: str
    unhyphenized_word: str


class OCRResultWriter:
    def __init__(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
        self.parts: List[TextPart] = []
        self.buffer_word: bool = False

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

    def _write_word_symbols(
        self,
        cursor: QTextCursor,
        symbols: list,
        confidence_color_threshold: int,
        word_format: QTextCharFormat,
        is_hyphenated_word: bool = False,
    ) -> None:
        first_word_part_unhyphenized = ""
        for i, symbol in enumerate(symbols):
            # If the word is hyphenated, ignore the closing hyphen
            # if (
            #     is_hyphenated_word
            #     and i == len(symbols) - 1
            #     and symbol.get_text() == "-"
            # ):
            #     continue

            symbol_format = QTextCharFormat(
                word_format
            )  # Inherit word-level formatting
            self._set_confidence_color_background(
                symbol_format, symbol, confidence_color_threshold
            )
            cursor.insertText(symbol.get_text(), symbol_format)

            # Check if next symbol is a hyphen and this is the last symbol in the word
            if (
                i < len(symbols) - 1
                and symbols[i + 1].get_text() == "-"
                and is_hyphenated_word
            ):
                first_word_part_unhyphenized = self.document.toHtml()

        if is_hyphenated_word:
            if self.buffer_word:
                # Store the the first and last part of the hyphenated word
                self.parts.append(self._store_document_state(TextPartType.HYPHENATED_WORD))
                self.buffer_word = False
            else:
                self.buffer_word = True

    def _reset_document(self) -> None:
        self.document = QTextDocument()
        self.cursor = QTextCursor(self.document)
        self.cursor.movePosition(QTextCursor.MoveOperation.Start)

    def _store_document_state(self, type: TextPartType, unhyphenized_text: str = ""
        part = TextPart(type, self.document.toHtml(), "")

        self._reset_document()

        return part

    def ocr_to_qdocument(
        self, ocr_result_blocks: list[OCRResultBlock]
    ) -> QTextDocument:
        self._reset_document()

        confidence_color_threshold = self.application_settings.get(
            "confidence_color_threshold", 50
        )

        first_block = True
        for block in ocr_result_blocks:
            if not first_block:
                self.cursor.insertBlock()

            first_block = False
            first_paragraph = True
            is_hyphenated_word = False

            for paragraph in block.paragraphs:
                if not first_paragraph:
                    self.cursor.insertBlock()
                first_paragraph = False

                for line in paragraph.lines:
                    for i, word in enumerate(line.words):
                        # Look ahead to check if the current word is the first or last word of a line
                        if i == len(line.words) - 1:
                            # ... and if it ends with a hyphen
                            if word.symbols[-1].get_text() == "-":
                                self.parts.append(
                                    self._store_document_state(TextPartType.TEXT)
                                )
                                is_hyphenated_word = True

                        word_format = QTextCharFormat()
                        self._set_confidence_color_background(
                            word_format, word, confidence_color_threshold
                        )

                        self._write_word_symbols(
                            self.cursor,
                            word.symbols,
                            confidence_color_threshold,
                            word_format,
                            is_hyphenated_word,
                        )

                        if i == 0:
                            # Beginning of the next line, so this is the second part of the hyphenated word
                            is_hyphenated_word = False

                        if word != line.words[-1]:
                            self.cursor.insertText(" ", QTextCharFormat())
                    if line != paragraph.lines[-1] and not is_hyphenated_word:
                        self.cursor.insertText(" ", QTextCharFormat())
            if block != ocr_result_blocks[-1]:
                self.cursor.insertText("\n", QTextCharFormat())

        # Append the last part
        self.parts.append(self._store_document_state(TextPartType.TEXT))

        # Merge the parts
        for part in self.parts:
            self.cursor.insertHtml(part.text)

        return self.document
