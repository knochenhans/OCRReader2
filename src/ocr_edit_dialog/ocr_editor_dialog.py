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
from typing import List, Optional, Tuple

from ocr_edit_dialog.token_type import TokenType  # type: ignore
from .draggable_image_label import DraggableImageLabel  # type: ignore

from .line_break_helper import LineBreakHelper, PartType, PartInfo
from .token import Token  # type: ignore
from page.page import Page  # type: ignore
from page.ocr_box import OCRBox, TextBox  # type: ignore


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


class OCREditorDialog(QDialog):
    def __init__(self, pages: List[Page], language: str) -> None:
        super().__init__()

        self.pages = pages
        self.language = language

        self.ocr_box: Optional[TextBox] = None

        self.setWindowTitle("OCR Editor")

        self.resize(1000, 600)

        self.main_layout: QHBoxLayout = QHBoxLayout()

        self.left_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.left_layout.addWidget(self.text_edit)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        # Page Navigation

        self.page_left_button: QPushButton = QPushButton("<<", self)
        self.page_left_button.clicked.connect(self.previous_page)
        self.button_layout.addWidget(self.page_left_button)

        self.page_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.page_label)

        self.page_right_button: QPushButton = QPushButton(">>", self)
        self.page_right_button.clicked.connect(self.next_page)
        self.button_layout.addWidget(self.page_right_button)

        # Box Navigation

        self.left_button: QPushButton = QPushButton("<", self)
        self.left_button.clicked.connect(self.previous_box)
        self.button_layout.addWidget(self.left_button)

        self.box_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.box_label)

        self.right_button: QPushButton = QPushButton(">", self)
        self.right_button.clicked.connect(self.next_box)
        self.button_layout.addWidget(self.right_button)

        self.apply_button: QPushButton = QPushButton("Finish", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.revert_button: QPushButton = QPushButton("Revert to OCR", self)
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

        self.page_box_count: int = 0
        self.applied_boxes: List[bool] = []

        self.current_page_index = -1
        self.current_box_index = -1
        self.current_absolute_box_index = -1

        self.text_boxes: List[Tuple[TextBox, int, int]] = []

        for i, page in enumerate(self.pages):
            for j, box in enumerate(page.layout.ocr_boxes):
                if isinstance(box, TextBox):
                    self.text_boxes.append((box, i, j))

        first_box = self.find_next_box()

        if first_box:
            self.load_box(first_box)
        else:
            self.close()

    def find_next_box(self) -> Optional[TextBox]:
        for i, (box, page_index, box_index) in enumerate(self.text_boxes):
            if i < self.current_absolute_box_index:
                continue

            self.current_page_index = page_index
            self.current_box_index = box_index
            self.current_absolute_box_index = i
            self.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
            return box
        return None

    def find_previous_box(self) -> Optional[TextBox]:
        for i, (box, page_index, box_index) in reversed(
            list(enumerate(self.text_boxes))
        ):
            if i > self.current_absolute_box_index:
                continue

            self.current_page_index = page_index
            self.current_box_index = box_index
            self.current_absolute_box_index = i
            self.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
            return box
        return None

    def load_box(self, box: TextBox) -> None:
        self.ocr_box = box

        self.applied_boxes = [False] * self.page_box_count

        self.line_break_helper: LineBreakHelper = LineBreakHelper(self.language)

        self.update_navigation_labels()
        self.set_processed_text()

        image_path = self.pages[self.current_page_index].image_path

        if not self.ocr_box:
            return

        if image_path:
            image = QPixmap(image_path)
            box_image_region = self.ocr_box.get_image_region()
            image = image.copy(
                box_image_region["x"],
                box_image_region["y"],
                box_image_region["width"],
                box_image_region["height"],
            )
            self.image_label.setPixmap(image)

    def update_navigation_labels(self) -> None:
        self.box_label.setText(
            f"Block {self.current_box_index + 1} of {self.page_box_count}"
        )
        self.page_label.setText(
            f"Page {self.current_page_index + 1} of {len(self.pages)}"
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

                            if self.line_break_helper.check_spelling(merged_word):
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

        # if not self.applied_boxes[self.current_box_index] and split_words_found:
        #     tokens_result = self.line_break_helper.show_line_break_table_dialog(tokens)
        #     if tokens_result != tokens:
        #         self.applied_boxes[self.current_box_index] = True
        #         tokens = tokens_result

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
    def next_box(self) -> None:
        self.current_absolute_box_index += 1

        next_box = self.find_next_box()
        if next_box:
            self.update_block_user_text()
            self.update_navigation_buttons()
            self.load_box(next_box)
        else:
            self.current_absolute_box_index = len(self.text_boxes) - 1

    @Slot()
    def previous_box(self) -> None:
        self.current_absolute_box_index -= 1

        previous_box = self.find_previous_box()
        if previous_box:
            self.update_block_user_text()
            self.update_navigation_buttons()
            self.load_box(previous_box)
        else:
            self.current_absolute_box_index = 0

    @Slot()
    def next_page(self) -> None:
        # box_index = self.current_absolute_box_index
        # while True:
        #     box_index += 1

        #     box, page_index, box_index = self.text_boxes[box_index]

        #     if page_index != self.current_page_index:
        #         self.current_absolute_box_index = box_index
        #         self.update_block_user_text()
        #         self.load_box(box)
        #         break

        #     if box_index == len(self.text_boxes) - 1:
        #         break
        pass

    @Slot()
    def previous_page(self) -> None:
        pass

    def update_navigation_buttons(self) -> None:
        self.left_button.setEnabled(self.current_absolute_box_index > 0)
        self.right_button.setEnabled(
            self.current_absolute_box_index < len(self.text_boxes) - 1
        )

        self.page_left_button.setEnabled(self.current_page_index > 0)
        self.page_right_button.setEnabled(self.current_page_index < len(self.pages) - 1)

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
