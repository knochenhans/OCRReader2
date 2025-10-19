from typing import List, Optional

from PySide6.QtCore import Slot

from page.ocr_box import TextBox


class OCREditorNavigationBoxes:
    def __init__(self, boxes: List[TextBox], dialog: "OCREditorDialogMerged") -> None:
        self.boxes = boxes
        self.dialog = dialog

        self.current_box_index = -1

    def find_next_box(self) -> Optional[TextBox]:
        if self.current_box_index + 1 < len(self.boxes):
            self.current_box_index += 1
            return self.boxes[self.current_box_index]
        return None

    def find_previous_box(self) -> Optional[TextBox]:
        if self.current_box_index - 1 >= 0:
            self.current_box_index -= 1
            return self.boxes[self.current_box_index]
        return None

    @Slot()
    def next_box(self) -> None:
        next_box = self.find_next_box()
        if next_box:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            self.dialog.load_box(next_box)
        else:
            self.current_box_index = len(self.boxes) - 1

    @Slot()
    def previous_box(self) -> None:
        previous_box = self.find_previous_box()
        if previous_box:
            self.dialog.update_block_user_text()
            self.dialog.update_navigation_buttons()
            self.dialog.load_box(previous_box)
        else:
            self.current_box_index = 0

    def move_to_first_box(self) -> None:
        if self.boxes:
            self.current_box_index = 0
            first_box = self.boxes[self.current_box_index]
            self.dialog.load_box(first_box)

    def move_to_last_box(self) -> None:
        if self.boxes:
            self.current_box_index = len(self.boxes) - 1
            last_box = self.boxes[self.current_box_index]
            self.dialog.load_box(last_box)
