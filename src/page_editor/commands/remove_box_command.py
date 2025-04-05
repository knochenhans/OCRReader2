from typing import Optional, Tuple

from loguru import logger
from PySide6.QtGui import QUndoCommand

from page.box_type import BoxType  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore


class RemoveBoxCommand(QUndoCommand):
    def __init__(
        self,
        box_id: str,
        controller: PageEditorController,
    ) -> None:
        super().__init__("Remove Box")
        self.box_id: str = box_id
        self.controller: PageEditorController = controller
        self.box_data: Optional[Tuple[Tuple[int, int, int, int], BoxType, int]] = None

        logger.debug(f"Added remove box command for box {self.box_id}")

    def undo(self) -> None:
        if self.box_data:
            region, box_type, order = self.box_data
            logger.debug(f"Undoing remove box command for box {self.box_id}")
            self.controller._add_box(region, box_type, order, box_id=self.box_id)

    def redo(self) -> None:
        logger.debug(f"Redoing remove box command for box {self.box_id}")
        box_data = self.controller._remove_box(self.box_id)
        if box_data is None:
            logger.error("Failed to remove box: remove_box returned None")
            self.box_data = None
        else:
            self.box_data = box_data
