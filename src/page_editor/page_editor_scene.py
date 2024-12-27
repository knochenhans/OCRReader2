from typing import Optional
from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page.ocr_box import OCRBox  # type: ignore


class PageEditorScene(QGraphicsScene):
    def __init__(self, controller: Optional[PageEditorController] = None) -> None:
        super().__init__()
        self.controller = controller
        self.boxes: dict[str, QGraphicsRectItem] = {}

    def add_box(self, box: OCRBox) -> None:
        rect_item = QGraphicsRectItem(box.x, box.y, box.width, box.height)
        rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.addItem(rect_item)
        self.boxes[box.id] = rect_item
