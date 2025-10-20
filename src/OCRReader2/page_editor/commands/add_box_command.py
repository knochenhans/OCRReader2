from typing import Tuple

from loguru import logger
from PySide6.QtGui import QUndoCommand

from OCRReader2.page.box_type import BoxType
from OCRReader2.page_editor.page_editor_controller import PageEditorController


class AddBoxCommand(QUndoCommand):
    def __init__(
        self,
        region: Tuple[int, int, int, int],
        box_type: BoxType,
        order: int,
        controller: PageEditorController,
    ) -> None:
        super().__init__("Add Box")
        self.region: Tuple[int, int, int, int] = region
        self.box_type: BoxType = box_type
        self.order: int = order
        self.controller: PageEditorController = controller
        self.box_id: str = ""

        logger.debug(
            f"Added add box command with region {self.region}, type {self.box_type}, order {self.order}"
        )

    def undo(self) -> None:
        if self.box_id:
            logger.debug(f"Undoing add box command for box {self.box_id}")
            self.controller._remove_box(self.box_id)

    def redo(self) -> None:
        logger.debug(f"Redoing add box command with region {self.region}")
        box_id = self.controller._add_box(self.region, self.box_type, self.order)
        if box_id is None:
            logger.error("Failed to add box: add_box returned None")
            self.box_id = ""
        else:
            self.box_id = box_id
