from loguru import logger
from PySide6.QtCore import QPointF
from PySide6.QtGui import QUndoCommand

from page_editor.page_editor_scene import PageEditorScene


class MoveBoxCommand(QUndoCommand):
    def __init__(
        self, box_id: str, old_pos: QPointF, new_pos: QPointF, scene: PageEditorScene
    ):
        super().__init__("Move Box")
        self.box_id = box_id
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.scene = scene

        logger.debug(
            f"Added move box command for box {self.box_id} from {self.old_pos} to {self.new_pos}"
        )

    def undo(self):
        logger.debug(
            f"Undoing move box command for box {self.box_id} from {self.new_pos} to {self.old_pos}"
        )
        box_item = self.scene.boxes.get(self.box_id)
        if box_item:
            self.scene.box_moving_programmatically = True
            box_item.setPos(self.old_pos)
            # self.scene.on_box_item_moved(self.box_id, self.old_pos)
            self.scene.box_moving_programmatically = False
        else:
            logger.error(f"Failed to undo move: box {self.box_id} not found")

    def redo(self):
        logger.debug(
            f"Redoing move box command for box {self.box_id} from {self.old_pos} to {self.new_pos}"
        )
        box_item = self.scene.boxes.get(self.box_id)
        if box_item:
            self.scene.box_moving_programmatically = True
            box_item.setPos(self.new_pos)
            # self.scene.on_box_item_moved(self.box_id, self.new_pos)
            self.scene.box_moving_programmatically = False
        else:
            logger.error(f"Failed to redo move: box {self.box_id} not found")
