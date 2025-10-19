from typing import List, Optional, Tuple

from PySide6.QtCore import Slot

from OCRReader2.ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog
from OCRReader2.page.ocr_box import TextBox
from OCRReader2.page.page import Page


class OCREditorNavigation:
    def __init__(self, pages: List[Page], dialog: Optional[OCREditorDialog]) -> None:
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

            if self.dialog:
                self.dialog.page_box_count = len(
                    self.pages[page_index].layout.ocr_boxes
                )
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

            if self.dialog:
                self.dialog.page_box_count = len(
                    self.pages[page_index].layout.ocr_boxes
                )
            return box
        return None

    @Slot()
    def next_box(self) -> None:
        self.current_absolute_box_index += 1

        next_box = self.find_next_box()
        if next_box and self.dialog:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            self.dialog.load_box(next_box)
        else:
            self.current_absolute_box_index = len(self.all_text_boxes) - 1

    @Slot()
    def previous_box(self) -> None:
        self.current_absolute_box_index -= 1

        previous_box = self.find_previous_box()
        if previous_box and self.dialog:
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

        if self.current_absolute_box_index != original_page_index and self.dialog:
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

        if self.current_absolute_box_index != original_page_index and self.dialog:
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
        if first_box and self.dialog:
            self.dialog.load_box(first_box)

    def move_to_last_page_block(self) -> None:
        while (
            self.current_absolute_box_index < len(self.all_text_boxes) - 1
            and self.all_text_boxes[self.current_absolute_box_index + 1][1]
            == self.current_page_index
        ):
            self.current_absolute_box_index += 1
