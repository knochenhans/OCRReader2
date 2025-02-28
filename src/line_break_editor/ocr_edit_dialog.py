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
from typing import List, Optional

from line_break_editor.token_type import TokenType  # type: ignore
from .draggable_image_label import DraggableImageLabel  # type: ignore

from .line_break_helper import LineBreakHelper, PartType, PartInfo
from .token import Token  # type: ignore
from page.page import Page  # type: ignore
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

        self.apply_button: QPushButton = QPushButton("Finish", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.revert_button: QPushButton = QPushButton("Revert", self)
        self.revert_button.clicked.connect(lambda: self.set_processed_text(True))
        self.button_layout.addWidget(self.revert_button)

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

        self.current_block_index = 0

        self.text_blocks: List[TextBox] = [
            box for box in self.page.layout.ocr_boxes if isinstance(box, TextBox)
        ]
        self.block_count = len(self.text_blocks)
        self.applied_blocks: List[bool] = [False] * self.block_count

        self.load_block(self.current_block_index)

        self.ocr_box: Optional[TextBox] = None

    def load_block(self, block_index: int) -> None:
        self.ocr_box = self.text_blocks[block_index]

        if not isinstance(self.ocr_box, TextBox):
            return

        self.line_break_helper: LineBreakHelper = LineBreakHelper(self.language)

        if not self.ocr_box.ocr_results:
            return

        self.paragraph_count = len(self.ocr_box.ocr_results.paragraphs)
        self.current_paragraph_index = 0
        self.update_block_label()

        if not self.ocr_box.ocr_results:
            return

        self.set_processed_text()

        if self.page.image_path:
            image = QPixmap(self.page.image_path)
            box_image_region = self.ocr_box.get_image_region()
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

        if not self.ocr_box:
            return

        if self.ocr_box.user_text and not revert:
            cursor.insertText(self.ocr_box.user_text)
            return

        self.default_format: QTextCharFormat = QTextCharFormat()

        merge_buffer = None

        if not self.ocr_box.ocr_results:
            return

        tokens: List[Token] = []

        split_words_found = False

        for paragraph in self.ocr_box.ocr_results.paragraphs:
            for line in paragraph.lines:
                for word in line.words:
                    if word == line.words[-1] and line != paragraph.lines[-1]:
                        if word.text.endswith("-"):
                            merge_buffer = word
                            split_words_found = True
                            continue

                    if merge_buffer:
                        unmerged_word = merge_buffer.text + word.text
                        if word.text[0].isupper():
                            token = Token(
                                TokenType.TEXT,
                                unmerged_word,
                                "",
                                False,
                                QColor(),
                            )
                        else:
                            r, g, b, a = merge_buffer.get_confidence_color(50)
                            color = QColor(r, g, b, a)
                            merged_word = merge_buffer.text[:-1] + word.text

                            stripped_merged_word = "".join(
                                e for e in merged_word if e.isalnum()
                            )
                            if self.line_break_helper.check_spelling(
                                stripped_merged_word
                            ):
                                color = QColor(0, 255, 0, 50)
                                token = Token(
                                    TokenType.SPLIT_WORD,
                                    merged_word,
                                    unmerged_word,
                                    True,
                                    color,
                                )
                            else:
                                color = QColor(0, 0, 255, 50)
                                token = Token(
                                    TokenType.SPLIT_WORD,
                                    merged_word,
                                    unmerged_word,
                                    True,
                                    color,
                                )

                        tokens.append(token)

                        merge_buffer = None
                    else:
                        r, g, b, a = word.get_confidence_color(50)
                        color = QColor(r, g, b, a)
                        token = Token(TokenType.TEXT, word.text, "", False, color)
                        tokens.append(token)

                    if line != line.words[-1]:
                        token = Token(TokenType.TEXT, " ", "", False, QColor())
                        tokens.append(token)
            if paragraph != self.ocr_box.ocr_results.paragraphs[-1]:
                token = Token(TokenType.TEXT, "\n", "", False, QColor())
                tokens.append(token)

        if not self.applied_blocks[self.current_block_index] and split_words_found:
            tokens_result = self.line_break_helper.show_line_break_table_dialog(tokens)
            if tokens_result != tokens:
                self.applied_blocks[self.current_block_index] = True
                tokens = tokens_result

        for token in tokens:
            format = QTextCharFormat()
            if token.text.strip() != "":
                format.setBackground(token.color)
            cursor.setCharFormat(format)

            text = token.text

            if token.token_type == TokenType.SPLIT_WORD:
                if not token.is_split_word:
                    text = token.unmerged_text

            cursor.insertText(text)

            cursor.setCharFormat(self.default_format)

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
        for i, part in enumerate(self.current_parts):
            part_info = PartInfo(
                part_type=part.part_type,
                unmerged_text=part.unmerged_text,
                merged_text=part.merged_text,
                is_in_dictionary=part.is_in_dictionary,
                use_merged=part.use_merged,
                ocr_result_word_1=part.ocr_result_word_1,
                ocr_result_word_2=part.ocr_result_word_2,
            )
            if part.part_type == PartType.WORD and not part.use_merged:
                self.current_parts[i] = self.line_break_helper.check_merged_word(
                    part_info
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
        for i, part in enumerate(self.current_parts):
            part_type = part.part_type
            part_unmerged = part.unmerged_text
            part_merged = part.merged_text
            is_in_dictionary = part.is_in_dictionary
            use_merged = part.use_merged
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
                part_info = self.current_parts[index]
                self.current_parts[index] = PartInfo(
                    part_type=part_info.part_type,
                    unmerged_text=part_info.unmerged_text,
                    merged_text=part_info.merged_text,
                    is_in_dictionary=part_info.is_in_dictionary,
                    use_merged=not part_info.use_merged,
                    ocr_result_word_1=part_info.ocr_result_word_1,
                    ocr_result_word_2=part_info.ocr_result_word_2,
                )

                self.update_editor_text()

    @Slot()
    def apply_changes(self) -> None:
        self.update_block_user_text()
        self.accept()

    def update_block_user_text(self) -> None:
        if self.ocr_box:
            self.ocr_box.user_text = self.get_text()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
