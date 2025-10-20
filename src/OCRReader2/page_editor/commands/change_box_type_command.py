from typing import List

from loguru import logger
from PySide6.QtGui import QUndoCommand

from OCRReader2.page.box_type import BoxType
from OCRReader2.page_editor.box_item import BoxItem
from OCRReader2.page_editor.page_editor_controller import PageEditorController


class ChangeMultipleBoxesTypeCommand(QUndoCommand):
    def __init__(
        self,
        box_items: List[BoxItem],
        new_box_type: BoxType,
        controller: PageEditorController,
    ) -> None:
        super().__init__("Change Multiple Box Types")
        self.child_commands: List[ChangeBoxTypeCommand] = []
        old_box_types: List[BoxType] = self._get_box_types(box_items, controller)
        for box in box_items:
            self.child_commands.append(
                ChangeBoxTypeCommand(
                    box, new_box_type, old_box_types[box_items.index(box)], controller
                )
            )

    def undo(self) -> None:
        for command in self.child_commands:
            command.undo()

    def redo(self) -> None:
        for command in self.child_commands:
            command.redo()

    def _get_box_types(
        self, box_items: List[BoxItem], controller: PageEditorController
    ) -> List[BoxType]:
        old_box_types: List[BoxType] = []

        for box_item in box_items:
            ocr_box = controller.page.layout.get_ocr_box_by_id(box_item.box_id)
            if ocr_box:
                ocr_box_type: BoxType = ocr_box.type
                old_box_types.append(ocr_box_type)

        return old_box_types


class ChangeBoxTypeCommand(QUndoCommand):
    def __init__(
        self,
        box_item: BoxItem,
        new_box_type: BoxType,
        old_box_type: BoxType,
        controller: PageEditorController,
    ) -> None:
        super().__init__("Change Box Type")
        self.box_item: BoxItem = box_item
        self.new_box_type: BoxType = new_box_type
        self.old_box_type: BoxType = old_box_type
        self.controller: PageEditorController = controller

        logger.debug(
            f"Added change box type command for box {self.box_item.box_id} from {self.old_box_type} to {self.new_box_type}"
        )

    def undo(self) -> None:
        logger.debug(f"Undoing change box type command for box {self.box_item.box_id}")
        self.controller.change_box_type(self.box_item.box_id, self.old_box_type)

    def redo(self) -> None:
        logger.debug(f"Redoing change box type command for box {self.box_item.box_id}")
        self.controller.change_box_type(self.box_item.box_id, self.new_box_type)
