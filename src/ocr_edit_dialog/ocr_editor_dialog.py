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
    QKeyEvent,
    QTextCursor,
    QTextCharFormat,
    QContextMenuEvent,
    QPixmap,
    QFont,
    QPainter,
    QPen,
)
from PySide6.QtCore import Slot, Signal, Qt
from typing import List, Optional, Tuple

from ocr_edit_dialog.token_type import TokenType  # type: ignore
from settings import Settings  # type: ignore
from .draggable_image_label import DraggableImageLabel  # type: ignore

from .line_break_helper import LineBreakHelper, PartType, PartInfo
from .token import Token  # type: ignore
from page.page import Page  # type: ignore
from page.ocr_box import OCRBox, TextBox  # type: ignore


class ClickableTextEdit(QTextEdit):
    linkRightClicked = Signal(str)
    ctrlEnterPressed = Signal()

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

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.ctrlEnterPressed.emit()
        else:
            super().keyPressEvent(event)


class OCREditorNavigation:
    def __init__(self, pages: List[Page], dialog) -> None:
        self.pages = pages
        self.dialog = dialog

        self.current_page_index = -1
        self.current_box_index = -1
        self.current_absolute_box_index = -1

        self.all_text_boxes: List[Tuple[TextBox, int, int]] = []

        for i, page in enumerate(self.pages):
            for j, box in enumerate(page.layout.ocr_boxes):
                if isinstance(box, TextBox):
                    self.all_text_boxes.append((box, i, j))

    def find_next_box(self) -> Optional[TextBox]:
        for i, (box, page_index, box_index) in enumerate(self.all_text_boxes):
            if i < self.current_absolute_box_index:
                continue

            self.current_page_index = page_index
            self.current_box_index = box_index
            self.current_absolute_box_index = i
            self.dialog.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
            return box
        return None

    def find_previous_box(self) -> Optional[TextBox]:
        for i, (box, page_index, box_index) in reversed(
            list(enumerate(self.all_text_boxes))
        ):
            if i > self.current_absolute_box_index:
                continue

            self.current_page_index = page_index
            self.current_box_index = box_index
            self.current_absolute_box_index = i
            self.dialog.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
            return box
        return None

    @Slot()
    def next_box(self) -> None:
        self.current_absolute_box_index += 1

        next_box = self.find_next_box()
        if next_box:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            self.dialog.load_box(next_box)
        else:
            self.current_absolute_box_index = len(self.all_text_boxes) - 1

    @Slot()
    def previous_box(self) -> None:
        self.current_absolute_box_index -= 1

        previous_box = self.find_previous_box()
        if previous_box:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            self.dialog.load_box(previous_box)
        else:
            self.current_absolute_box_index = 0

    @Slot()
    def next_page(self) -> None:
        original_page_index = self.current_page_index

        while (
            self.current_absolute_box_index < len(self.all_text_boxes)
            and self.current_page_index
            == self.all_text_boxes[self.current_absolute_box_index][1]
        ):
            self.current_absolute_box_index += 1

        if self.current_absolute_box_index != original_page_index:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            next_box = self.find_next_box()
            if next_box:
                self.dialog.load_box(next_box)
            else:
                self.current_absolute_box_index = len(self.all_text_boxes) - 1

    @Slot()
    def previous_page(self) -> None:
        original_page_index = self.current_page_index

        while (
            self.current_absolute_box_index >= 0
            and self.current_page_index
            == self.all_text_boxes[self.current_absolute_box_index][1]
        ):
            self.current_absolute_box_index -= 1

        if self.current_absolute_box_index != original_page_index:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            previous_box = self.find_previous_box()
            if previous_box:
                self.dialog.load_box(previous_box)
            else:
                self.current_absolute_box_index = 0

            self.move_to_first_page_block()

    def move_to_first_page_block(self) -> None:
        while (
            self.current_absolute_box_index > 0
            and self.all_text_boxes[self.current_absolute_box_index - 1][1]
            == self.current_page_index
        ):
            self.current_absolute_box_index -= 1

        first_box = self.find_next_box()
        if first_box:
            self.dialog.load_box(first_box)

    def move_to_last_page_block(self) -> None:
        while (
            self.current_absolute_box_index < len(self.all_text_boxes) - 1
            and self.all_text_boxes[self.current_absolute_box_index + 1][1]
            == self.current_page_index
        ):
            self.current_absolute_box_index += 1


class OCREditorDialog(QDialog):
    def __init__(
        self,
        pages: List[Page],
        language: str,
        application_settings: Settings,
        start_box_id: str,
        for_project=False,
    ) -> None:
        super().__init__()

        self.pages = pages
        self.language = language
        self.application_settings = application_settings

        self.ocr_box: Optional[TextBox] = None

        if for_project:
            self.setWindowTitle("OCR Editor (Project)")
        else:
            self.setWindowTitle("OCR Editor")

        self.resize(1000, 600)

        self.main_layout: QHBoxLayout = QHBoxLayout()
        self.left_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        if self.application_settings:
            background_color = self.application_settings.get(
                "editor_background_color", "white"
            )
            text_color = self.application_settings.get("editor_text_color", "black")
            font = self.application_settings.get("editor_font", QFont())
            self.text_edit.setStyleSheet(
                f"background-color: {QColor(background_color).name()}; color: {QColor(text_color).name()};"
            )
            self.text_edit.setFont(font)
        else:
            self.text_edit.setStyleSheet("background-color: white; color: black;")
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.text_edit.ctrlEnterPressed.connect(self.move_forward)
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

        self.image_label = DraggableImageLabel(self)
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

        self.navigation = OCREditorNavigation(self.pages, self)

        if start_box_id:
            for i, (box, page_index, box_index) in enumerate(
                self.navigation.all_text_boxes
            ):
                if box.id == start_box_id:
                    first_box = box
                    self.navigation.current_page_index = page_index
                    self.navigation.current_box_index = box_index
                    self.navigation.current_absolute_box_index = i
                    self.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
                    break
        else:
            first_box = self.navigation.find_next_box()

        if first_box:
            self.load_box(first_box)
        else:
            self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            event.key() == Qt.Key.Key_Right
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.next_box()
        elif (
            event.key() == Qt.Key.Key_Left
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.previous_box()
        elif (
            event.key() == Qt.Key.Key_PageUp
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.next_page()
        elif (
            event.key() == Qt.Key.Key_PageDown
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.previous_page()
        else:
            super().keyPressEvent(event)

    def move_forward(self) -> None:
        # Move to next box or apply changes if there are no more boxes
        if (
            self.navigation.current_absolute_box_index
            < len(self.navigation.all_text_boxes) - 1
        ):
            self.next_box()
        else:
            self.apply_changes()

    def load_box(self, box: TextBox) -> None:
        self.ocr_box = box

        self.applied_boxes = [False] * self.page_box_count

        self.line_break_helper: LineBreakHelper = LineBreakHelper(self.language)

        self.update_navigation_labels()
        self.set_processed_text()

        image_path = self.pages[self.navigation.current_page_index].image_path

        if not self.ocr_box:
            return

        ocr_results = self.ocr_box.ocr_results

        if not ocr_results:
            return

        word_boxes = []

        confidence_color_threshold = self.application_settings.get(
            "confidence_color_threshold", 75.0
        )

        box_image_region = self.ocr_box.get_image_region()

        for paragraph in ocr_results.paragraphs:
            for line in paragraph.lines:
                for word in line.words:
                    if word.confidence < confidence_color_threshold:
                        if word.bbox:
                            mapped_bbox = (
                                word.bbox[0] - box_image_region["x"],
                                word.bbox[1] - box_image_region["y"],
                                word.bbox[2] - word.bbox[0],
                                word.bbox[3] - word.bbox[1],
                            )
                            word_boxes.append(
                                (
                                    mapped_bbox,
                                    word.get_confidence_color(
                                        confidence_color_threshold
                                    ),
                                )
                            )

        self.image_label.set_boxes(word_boxes)

        if image_path:
            image = QPixmap(image_path)
            image = image.copy(
                box_image_region["x"],
                box_image_region["y"],
                box_image_region["width"],
                box_image_region["height"],
            )
            self.image_label.setPixmap(image)

    def update_navigation_labels(self) -> None:
        self.box_label.setText(
            f"Block {self.navigation.current_box_index + 1} of {self.page_box_count}"
        )
        self.page_label.setText(
            f"Page {self.navigation.current_page_index + 1} of {len(self.pages)}"
        )

    def set_processed_text(self, revert=False) -> None:
        confidence_color_threshold = self.application_settings.get(
            "confidence_color_threshold", 0.0
        )

        document = self.text_edit.document()
        document.clear()
        cursor: QTextCursor = QTextCursor(document)

        if not self.ocr_box:
            return

        if self.ocr_box.user_text.strip() and not revert:
            cursor.insertText(self.ocr_box.user_text.strip())
            return

        self.default_format: QTextCharFormat = QTextCharFormat()

        merge_buffer = None

        if not self.ocr_box.ocr_results:
            return

        tokens: List[Token] = []

        split_words_found = False

        default_underline_color = self.default_format.underlineColor()
        default_background_color = self.default_format.background().color()
        default_font_color = self.default_format.foreground().color()

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
                                default_background_color,
                                default_font_color,
                            )
                        else:
                            r, g, b, a = merge_buffer.get_confidence_color(
                                confidence_color_threshold
                            )
                            background_color = QColor(r, g, b, a)
                            merged_word = merge_buffer.text[:-1] + word.text

                            if self.line_break_helper.check_spelling(merged_word):
                                # Word is in dictionary
                                underline_color = QColor(0, 255, 0, 50)

                                if self.application_settings:
                                    underline_color = QColor(
                                        self.application_settings.get(
                                            "merged_word_in_dict_color", underline_color
                                        )
                                    )

                                token = Token(
                                    TokenType.SPLIT_WORD,
                                    merged_word,
                                    unmerged_word,
                                    True,
                                    underline_color,
                                    background_color,
                                    default_font_color,
                                )
                            else:
                                # Word is not in dictionary
                                underline_color = QColor(0, 0, 255, 50)

                                if self.application_settings:
                                    underline_color = QColor(
                                        self.application_settings.get(
                                            "merged_word_not_in_dict_color",
                                            underline_color,
                                        )
                                    )

                                token = Token(
                                    TokenType.SPLIT_WORD,
                                    merged_word,
                                    unmerged_word,
                                    True,
                                    underline_color,
                                    background_color,
                                    default_font_color,
                                )

                        tokens.append(token)

                        merge_buffer = None
                    else:
                        r, g, b, a = word.get_confidence_color(
                            confidence_color_threshold
                        )
                        background_color = QColor(r, g, b, a)
                        token = Token(
                            TokenType.TEXT,
                            word.text,
                            "",
                            False,
                            default_underline_color,
                            background_color,
                            default_font_color,
                        )
                        tokens.append(token)

                    if line != line.words[-1]:
                        token = Token(
                            TokenType.TEXT,
                            " ",
                            "",
                            False,
                            default_underline_color,
                            default_background_color,
                            default_font_color,
                        )
                        tokens.append(token)
            if paragraph != self.ocr_box.ocr_results.paragraphs[-1]:
                token = Token(
                    TokenType.TEXT,
                    "\n",
                    "",
                    False,
                    default_underline_color,
                    default_background_color,
                    default_font_color,
                )
                tokens.append(token)

        # if not self.applied_boxes[self.navigation.current_box_index] and split_words_found:
        #     tokens_result = self.line_break_helper.show_line_break_table_dialog(tokens)
        #     if tokens_result != tokens:
        #         self.applied_boxes[self.navigation.current_box_index] = True
        #         tokens = tokens_result

        for token in tokens:
            format = QTextCharFormat()
            if token.text.strip() != "":
                format.setUnderlineColor(token.underline_color)
                if token.underline_color != default_underline_color:
                    format.setUnderlineStyle(
                        QTextCharFormat.UnderlineStyle.SingleUnderline
                    )
                if token.background_color != default_background_color:
                    format.setBackground(token.background_color)
                if token.font_color != default_font_color:
                    format.setForeground(token.font_color)
            cursor.setCharFormat(format)

            text = token.text

            if token.token_type == TokenType.SPLIT_WORD:
                if not token.is_split_word:
                    text = token.unmerged_text

            cursor.insertText(text)

            cursor.setCharFormat(self.default_format)

    @Slot()
    def next_box(self) -> None:
        self.navigation.next_box()

    @Slot()
    def previous_box(self) -> None:
        self.navigation.previous_box()

    @Slot()
    def next_page(self) -> None:
        self.navigation.next_page()

    @Slot()
    def previous_page(self) -> None:
        self.navigation.previous_page()

    def update_navigation_buttons(self) -> None:
        self.left_button.setEnabled(self.navigation.current_absolute_box_index > 0)
        self.right_button.setEnabled(
            self.navigation.current_absolute_box_index
            < len(self.navigation.all_text_boxes) - 1
        )

        self.page_left_button.setEnabled(self.navigation.current_page_index > 0)
        self.page_right_button.setEnabled(
            self.navigation.current_page_index < len(self.pages) - 1
        )

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
            self.ocr_box.user_text = self.get_text().strip()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
