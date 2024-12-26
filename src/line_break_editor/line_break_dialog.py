from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMenu,
    QHBoxLayout,
)
from PySide6.QtGui import QColor, QTextCursor, QTextCharFormat, QContextMenuEvent
from PySide6.QtCore import Slot, Signal
from typing import List

from .line_break_controller import LineBreakController, PartType, PartInfo
from page.ocr_box import TextBox  # type: ignore
from page.box_type import BoxType  # type: ignore


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
    def __init__(self) -> None:
        super().__init__()

        text_box = TextBox(0, 0, 0, 0, BoxType.FLOWING_TEXT)
        text_box.user_text = """Drei erstklassige Rennpfer-\nde hat Commodore mit den Amigas im Stall. Der Amiga 500 wird für frischen Wind in der gehobenen Heimcompu-\nterszene sorgen. Mit eingebau-\ntem Quatsch."""

        self.controller: LineBreakController = LineBreakController(text_box, "de")

        self.setWindowTitle("Simple Dialog")

        self.resize(800, 300)

        self.main_layout: QVBoxLayout = QVBoxLayout()

        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.main_layout.addWidget(self.text_edit)

        self.button_layout: QHBoxLayout = QHBoxLayout()

        self.apply_button: QPushButton = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.cancel_button: QPushButton = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        self.parts: List[PartInfo] = self.controller.remove_line_breaks()

        self.check_words()
        self.update_text()

    def check_words(self) -> None:
        for i, (
            part_type,
            part_unmerged,
            part_merged,
            is_in_dictionary,
            use_merged,
        ) in enumerate(self.parts):
            if part_type == PartType.WORD:
                if not use_merged:
                    self.parts[i] = self.controller.check_merged_word(
                        (
                            part_type,
                            part_unmerged,
                            part_merged,
                            is_in_dictionary,
                            use_merged,
                        )
                    )

    def update_text(self) -> None:
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
        ) in enumerate(self.parts):
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

            if index < len(self.parts):
                part_type, part_unmerged, part_merged, is_in_dictionary, use_merged = (
                    self.parts[index]
                )
                self.parts[index] = (
                    part_type,
                    part_unmerged,
                    part_merged,
                    is_in_dictionary,
                    not use_merged,
                )

                self.update_text()

    @Slot()
    def apply_changes(self) -> None:
        self.accept()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()
