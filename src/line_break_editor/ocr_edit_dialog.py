from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMenu,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)
from PySide6.QtGui import (
    QColor,
    QTextCursor,
    QTextCharFormat,
    QContextMenuEvent,
    QPixmap,
)
from PySide6.QtCore import Slot, Signal, Qt
from typing import List
import aspell  # type: ignore

from page.page import Page  # type: ignore
from .draggable_image_label import DraggableImageLabel  # type: ignore

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
    def __init__(self, page: Page, language: str) -> None:
        super().__init__()

        self.page = page
        self.language = language

        self.setWindowTitle("OCR Editor")

        self.resize(1000, 600)

        self.main_layout: QHBoxLayout = QHBoxLayout()

        self.left_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.left_layout.addWidget(self.text_edit)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        self.left_button: QPushButton = QPushButton("<", self)
        self.left_button.clicked.connect(self.previous_block)
        self.button_layout.addWidget(self.left_button)

        self.block_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.block_label)

        self.right_button: QPushButton = QPushButton(">", self)
        self.right_button.clicked.connect(self.next_block)
        self.button_layout.addWidget(self.right_button)

        self.revert_button: QPushButton = QPushButton("Revert", self)
        self.revert_button.clicked.connect(lambda: self.set_processed_text(True))
        self.button_layout.addWidget(self.revert_button)

        self.apply_button: QPushButton = QPushButton("Finish", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.cancel_button: QPushButton = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.left_layout.addLayout(self.button_layout)

        self.main_layout.addLayout(self.left_layout)

        self.image_label: QLabel = DraggableImageLabel(self)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.image_label.setMaximumHeight(self.height())
        self.image_label.setMinimumHeight(self.height())
        self.image_label.setMinimumWidth(int(self.width() / 3))
        self.main_layout.addWidget(
            self.image_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.setLayout(self.main_layout)

        self.current_parts: List[PartInfo] = []

        self.spell = aspell.Speller("lang", self.language)

        self.current_block_index = 0

        self.text_blocks: List[TextBox] = [
            box for box in self.page.layout.ocr_boxes if isinstance(box, TextBox)
        ]
        self.block_count = len(self.text_blocks)

        self.load_block(self.current_block_index)

    def load_block(self, block_index: int) -> None:
        box = self.text_blocks[block_index]

        if not isinstance(box, TextBox):
            return

        self.controller: OCREditController = OCREditController(box, self.language)

        if not self.controller.ocr_box.ocr_results:
            return

        self.paragraph_count = len(self.controller.ocr_box.ocr_results.paragraphs)
        self.current_paragraph_index = 0
        self.update_block_label()

        if not self.controller.ocr_box.ocr_results:
            return

        self.set_processed_text()

        if self.page.image_path:
            image = QPixmap(self.page.image_path)
            box_image_region = self.controller.ocr_box.get_image_region()
            image = image.copy(
                box_image_region["x"],
                box_image_region["y"],
                box_image_region["width"],
                box_image_region["height"],
            )
            self.image_label.setPixmap(image)

    def update_block_label(self) -> None:
        self.block_label.setText(
            f"Block {self.current_block_index + 1} of {self.block_count}"
        )

    def set_processed_text(self, revert=False) -> None:
        document = self.text_edit.document()
        document.clear()
        cursor: QTextCursor = QTextCursor(document)

        if self.controller.ocr_box.user_text and not revert:
            cursor.insertText(self.controller.ocr_box.user_text)
            return

        self.default_format: QTextCharFormat = QTextCharFormat()

        merge_buffer = None

        if not self.controller.ocr_box.ocr_results:
            return

        for paragraph in self.controller.ocr_box.ocr_results.paragraphs:
            # cursor.insertHtml("<p>")
            for line in paragraph.lines:
                for word in line.words:
                    if word == line.words[-1] and line != paragraph.lines[-1]:
                        if word.text.endswith("-"):
                            merge_buffer = word
                            continue

                    format = QTextCharFormat()
                    if merge_buffer:
                        r, g, b, a = merge_buffer.get_confidence_color(50)
                        a = 50

                        merged_word = merge_buffer.text[:-1] + word.text

                        stripped_merged_word = "".join(
                            e for e in merged_word if e.isalnum()
                        )
                        if self.spell.check(stripped_merged_word):
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
            if paragraph != self.controller.ocr_box.ocr_results.paragraphs[-1]:
                cursor.insertHtml("<br>")
            # cursor.insertHtml("</p>")

    @Slot()
    def next_block(self) -> None:
        self.current_block_index += 1
        if self.current_block_index >= self.block_count:
            self.current_block_index = self.block_count - 1

        self.update_block_user_text()
        self.update_navigation_buttons()
        self.load_block(self.current_block_index)

    @Slot()
    def previous_block(self) -> None:
        self.current_block_index -= 1
        if self.current_block_index < 0:
            self.current_block_index = 0

        self.update_block_user_text()
        self.update_navigation_buttons()
        self.load_block(self.current_block_index)

    def update_navigation_buttons(self) -> None:
        self.left_button.setEnabled(self.current_block_index > 0)
        self.right_button.setEnabled(self.current_block_index < self.block_count - 1)

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
        self.update_block_user_text()
        self.accept()

    def update_block_user_text(self) -> None:
        self.controller.ocr_box.user_text = self.get_text()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
