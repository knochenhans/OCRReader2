from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMenu,
    QHBoxLayout,
    QLabel,
)
from PySide6.QtGui import QColor, QTextCursor, QTextCharFormat, QContextMenuEvent
from PySide6.QtCore import Slot, Signal
from typing import List
import aspell  # type: ignore

from project.project import Project  # type: ignore

from .ocr_edit_controller import OCREditController, PartType, PartInfo  # type: ignore
from page.ocr_box import TextBox  # type: ignore


class ClickableTextEdit(QTextEdit):
    linkRightClicked = Signal(str)

    def mousePressEvent(self, e):
        self.anchor = self.anchorAt(e.pos())
        super().mousePressEvent(e)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        anchor = self.anchorAt(event.pos())
        if anchor:
            menu = QMenu(self)
            action = menu.addAction("Switch Hyphenation")
            action.triggered.connect(lambda: self.linkRightClicked.emit(anchor))
            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)


class OCREditDialog(QDialog):
    def __init__(self, project: Project, language: str) -> None:
        super().__init__()

        self.project = project
        self.language = language

        self.setWindowTitle("OCR Editor")

        self.resize(800, 300)

        self.main_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.main_layout.addWidget(self.text_edit)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        self.left_button: QPushButton = QPushButton("<", self)
        # self.left_button.clicked.connect(self.previous_paragraph)
        self.button_layout.addWidget(self.left_button)

        self.page_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.page_label)

        self.right_button: QPushButton = QPushButton(">", self)
        # self.right_button.clicked.connect(self.next_paragraph)
        self.button_layout.addWidget(self.right_button)

        self.apply_button: QPushButton = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.cancel_button: QPushButton = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        self.current_parts: List[PartInfo] = []

        self.spell = aspell.Speller("lang", self.language)

        self.load_block(0)

    def load_block(self, block_index: int) -> None:
        box = self.project.pages[0].layout.ocr_boxes[block_index]

        if not isinstance(box, TextBox):
            return

        self.controller: OCREditController = OCREditController(box, self.language)

        if not self.controller.ocr_box.ocr_results:
            return

        self.paragraph_count = len(self.controller.ocr_box.ocr_results.paragraphs)
        self.current_paragraph_index = 0
        # self.update_page_label()
        # self.load_paragraph(self.current_paragraph_index)

        if not self.controller.ocr_box.ocr_results:
            return

        document = self.text_edit.document()
        document.clear()
        cursor: QTextCursor = QTextCursor(document)

        self.default_format: QTextCharFormat = QTextCharFormat()

        merge_buffer = None

        for paragraph in self.controller.ocr_box.ocr_results.paragraphs:
            for line in paragraph.lines:
                for word in line.words:
                    if word == line.words[-1]:
                        if word.text.endswith("-"):
                            merge_buffer = word
                            continue

                    format = QTextCharFormat()
                    if merge_buffer:
                        r, g, b, a = merge_buffer.get_confidence_color(50)
                        a = 100

                        merged_word = merge_buffer.text[:-1] + word.text

                        if self.spell.check(merged_word):
                            text = merged_word
                            g = 255
                        else:
                            text = merge_buffer.text + word.text
                            b = 255

                        format.setBackground(QColor(r, g, b, a))
                        cursor.setCharFormat(format)
                        cursor.insertText(text)

                        merge_buffer = None
                    else:
                        r, g, b, a = word.get_confidence_color(50)
                        format.setBackground(QColor(r, g, b, a))
                        cursor.setCharFormat(format)
                        cursor.insertText(word.text)

                    cursor.setCharFormat(self.default_format)

                    if line != line.words[-1]:
                        cursor.insertText(" ")
         
                # if paragraph != paragraph.lines[-1]:
                #     cursor.insertText(" ")

            if paragraph != self.controller.ocr_box.ocr_results.paragraphs[-1]:
                cursor.insertText("\n")

    # def load_paragraph(self, paragraph_index: int) -> None:
    #     self.current_parts = []

    #     if self.controller.ocr_box.ocr_results:
    #         paragraph = self.controller.ocr_box.ocr_results.paragraphs[paragraph_index]

    #         if paragraph.user_text:
    #             self.text_edit.setPlainText(paragraph.user_text)
    #         else:
    #             self.current_parts = self.controller.remove_line_breaks(paragraph)
    #             self.check_words()
    #             self.update_editor_text()

    #     if self.current_paragraph_index == 0:
    #         self.left_button.setEnabled(False)
    #     else:
    #         self.left_button.setEnabled(True)

    #     if self.current_paragraph_index == self.paragraph_count - 1:
    #         self.right_button.setEnabled(False)
    #     else:
    #         self.right_button.setEnabled(True)

    # def update_paragraph(self) -> None:
    #     if self.controller.ocr_box.ocr_results:
    #         self.controller.ocr_box.ocr_results.paragraphs[
    #             self.current_paragraph_index
    #         ].user_text = self.text_edit.toPlainText()

    #     document = self.text_edit.document()
    #     document.clear()

    # def update_page_label(self) -> None:
    #     self.page_label.setText(
    #         f"{self.current_paragraph_index + 1} / {self.paragraph_count}"
    #     )

    # @Slot()
    # def previous_paragraph(self) -> None:
    #     self.update_paragraph()
    #     self.current_paragraph_index -= 1
    #     if self.current_paragraph_index < 0:
    #         self.current_paragraph_index = 0

    #     self.update_page_label()
    #     self.load_paragraph(self.current_paragraph_index)

    # @Slot()
    # def next_paragraph(self) -> None:
    #     self.update_paragraph()
    #     self.current_paragraph_index += 1
    #     if self.current_paragraph_index >= self.paragraph_count:
    #         self.current_paragraph_index = self.paragraph_count - 1

    #     self.update_page_label()
    #     self.load_paragraph(self.current_paragraph_index)

    def check_words(self) -> None:
        for i, (
            part_type,
            part_unmerged,
            part_merged,
            is_in_dictionary,
            use_merged,
            word,
            word,
        ) in enumerate(self.current_parts):
            if part_type == PartType.WORD:
                if not use_merged:
                    self.current_parts[i] = self.controller.check_merged_word(
                        (
                            part_type,
                            part_unmerged,
                            part_merged,
                            is_in_dictionary,
                            use_merged,
                            word,
                            word,
                        )
                    )

    def update_editor_text(self) -> None:
        document = self.text_edit.document()
        document.clear()

        # self.default_format: QTextCharFormat = QTextCharFormat()

        self.red_format: QTextCharFormat = QTextCharFormat()
        self.red_format.setForeground(QColor("red"))
        self.red_format.setAnchor(True)

        self.blue_format: QTextCharFormat = QTextCharFormat()
        self.blue_format.setForeground(QColor("blue"))
        self.blue_format.setAnchor(True)

        cursor: QTextCursor = QTextCursor(document)
        for i, (
            part_type,
            part_unmerged,
            part_merged,
            is_in_dictionary,
            use_merged,
            word,
            word,
        ) in enumerate(self.current_parts):
            current_href_index = i
            if part_type == PartType.WORD:
                format = QTextCharFormat()
                if is_in_dictionary:
                    format = self.blue_format
                    format.setAnchorHref(f"spell:{current_href_index}")
                else:
                    format = self.red_format
                    format.setAnchorHref(f"spell:{current_href_index}")

                if use_merged:
                    cursor.insertText(part_merged, format)
                else:
                    cursor.insertText(part_unmerged, format)
            else:
                cursor.insertText(part_unmerged, self.default_format)

    @Slot(str)
    def on_link_right_clicked(self, url: str) -> None:
        if url.startswith("spell:"):
            index = int(url.split(":")[1])

            if index < len(self.current_parts):
                (
                    part_type,
                    part_unmerged,
                    part_merged,
                    is_in_dictionary,
                    use_merged,
                    word,
                    word,
                ) = self.current_parts[index]
                self.current_parts[index] = (
                    part_type,
                    part_unmerged,
                    part_merged,
                    is_in_dictionary,
                    not use_merged,
                    word,
                    word,
                )

                self.update_editor_text()

    @Slot()
    def apply_changes(self) -> None:
        # self.update_paragraph()
        self.accept()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
