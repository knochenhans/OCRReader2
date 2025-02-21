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

from .line_break_controller import LineBreakController, PartType, PartInfo
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


class LineBreakDialog(QDialog):
    def __init__(self, text_box: TextBox, language: str) -> None:
        super().__init__()

        self.controller: LineBreakController = LineBreakController(text_box, language)

        self.setWindowTitle("Edit Line Breaks")

        self.resize(800, 300)

        self.main_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.main_layout.addWidget(self.text_edit)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        self.left_button: QPushButton = QPushButton("<", self)
        self.left_button.clicked.connect(self.previous_paragraph)
        self.button_layout.addWidget(self.left_button)

        self.page_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.page_label)

        self.right_button: QPushButton = QPushButton(">", self)
        self.right_button.clicked.connect(self.next_paragraph)
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

        if not self.controller.ocr_box.ocr_results:
            return

        self.paragraph_count = len(self.controller.ocr_box.ocr_results.paragraphs)
        self.current_paragraph_index = 0
        self.update_page_label()
        self.load_paragraph(self.current_paragraph_index)

    def load_paragraph(self, paragraph_index: int) -> None:
        self.current_parts = []

        if self.controller.ocr_box.ocr_results:
            paragraph = self.controller.ocr_box.ocr_results.paragraphs[paragraph_index]

            if paragraph.user_text:
                self.text_edit.setPlainText(paragraph.user_text)
            else:
                self.current_parts = self.controller.remove_line_breaks(
                    paragraph.get_text()
                )
                self.check_words()
                self.update_editor_text()

        if self.current_paragraph_index == 0:
            self.left_button.setEnabled(False)
        else:
            self.left_button.setEnabled(True)

        if self.current_paragraph_index == self.paragraph_count - 1:
            self.right_button.setEnabled(False)
        else:
            self.right_button.setEnabled(True)

    def update_paragraph(self) -> None:
        if self.controller.ocr_box.ocr_results:
            self.controller.ocr_box.ocr_results.paragraphs[
                self.current_paragraph_index
            ].user_text = self.text_edit.toPlainText()
        
        document = self.text_edit.document()
        document.clear()

    def update_page_label(self) -> None:
        self.page_label.setText(
            f"{self.current_paragraph_index + 1} / {self.paragraph_count}"
        )

    @Slot()
    def previous_paragraph(self) -> None:
        self.update_paragraph()
        self.current_paragraph_index -= 1
        if self.current_paragraph_index < 0:
            self.current_paragraph_index = 0

        self.update_page_label()
        self.load_paragraph(self.current_paragraph_index)

    @Slot()
    def next_paragraph(self) -> None:
        self.update_paragraph()
        self.current_paragraph_index += 1
        if self.current_paragraph_index >= self.paragraph_count:
            self.current_paragraph_index = self.paragraph_count - 1

        self.update_page_label()
        self.load_paragraph(self.current_paragraph_index)

    def check_words(self) -> None:
        for i, (
            part_type,
            part_unmerged,
            part_merged,
            is_in_dictionary,
            use_merged,
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
                        )
                    )

    def update_editor_text(self) -> None:
        document = self.text_edit.document()
        document.clear()

        self.default_format: QTextCharFormat = QTextCharFormat()

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
                part_type, part_unmerged, part_merged, is_in_dictionary, use_merged = (
                    self.current_parts[index]
                )
                self.current_parts[index] = (
                    part_type,
                    part_unmerged,
                    part_merged,
                    is_in_dictionary,
                    not use_merged,
                )

                self.update_editor_text()

    @Slot()
    def apply_changes(self) -> None:
        self.update_paragraph()
        self.accept()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
