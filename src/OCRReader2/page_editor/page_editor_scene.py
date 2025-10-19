import math
from typing import TYPE_CHECKING, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import QPointF, QRect, QRectF, QSizeF, Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSceneContextMenuEvent,
)
from SettingsManager import SettingsManager

from OCRReader2.page.box_type_color_map import BOX_TYPE_COLOR_MAP
from OCRReader2.page.ocr_box import OCRBox, TextBox
from OCRReader2.page_editor.box_item import BoxItem
from OCRReader2.page_editor.header_footer_item import (
    HEADER_FOOTER_ITEM_TYPE,
    HeaderFooterItem,
)

if TYPE_CHECKING:
    from OCRReader2.page_editor.page_editor_controller import PageEditorController


class PageEditorScene(QGraphicsScene):
    def __init__(
        self,
        application_settings: SettingsManager,
        controller: Optional["PageEditorController"] = None,
    ) -> None:
        super().__init__()
        self.controller = controller
        self.application_settings = application_settings
        self.boxes: Dict[str, BoxItem] = {}
        self.page_image_item: Optional[QGraphicsItem] = None
        self.header_item: Optional[HeaderFooterItem] = None
        self.footer_item: Optional[HeaderFooterItem] = None

        self.box_moving_programmatically = False

    def select_next_box(self) -> None:
        box_items = self.get_all_box_items()
        selected_items = self.get_selected_box_items()

        if len(selected_items) == 0:
            if len(box_items) > 0:
                box_items[0].setSelected(True)
        else:
            selected_index = box_items.index(selected_items[0])
            next_index = (selected_index + 1) % len(box_items)
            selected_items[0].setSelected(False)
            box_items[next_index].setSelected(True)

    def add_box_item_from_ocr_box(self, ocr_box: OCRBox) -> None:
        box_item = BoxItem(
            ocr_box.id,
            0,
            0,
            ocr_box.width,
            ocr_box.height,
            application_settings=self.application_settings,
        )
        box_item.set_color(BOX_TYPE_COLOR_MAP[ocr_box.type])

        if self.controller:
            box_item.box_moved.connect(self.on_box_item_moved)
            box_item.box_resized.connect(self.on_box_item_resized)
            box_item.box_double_clicked.connect(self.controller.on_box_double_clicked)

        self.addItem(box_item)
        box_item.setPos(ocr_box.x, ocr_box.y)
        box_item.order = ocr_box.order + 1

        if isinstance(ocr_box, TextBox):
            box_item.is_recognized = ocr_box.has_text()
            box_item.has_user_text = ocr_box.user_text.strip() != ""
            box_item.flows_into_next = ocr_box.flows_into_next
            box_item.has_user_data = ocr_box.user_data != {}

        self.boxes[ocr_box.id] = box_item

    def remove_box_item(self, box_id: str) -> None:
        if box_id in self.boxes:
            self.removeItem(self.boxes[box_id])
            del self.boxes[box_id]

    def on_box_item_moved(self, box_id: str, pos: QPointF) -> None:
        from OCRReader2.page_editor.commands.move_box_command import MoveBoxCommand

        if self.box_moving_programmatically:
            return

        if self.controller:
            logger.debug(f"Page box item {box_id} moved to {pos}")
            ocr_box = self.controller.page.layout.get_ocr_box_by_id(box_id)
            if ocr_box:
                old_pos = QPointF(ocr_box.x, ocr_box.y)  # Get the old position
                ocr_box.update_position(int(pos.x()), int(pos.y()), "GUI")

                # Push the move command to the undo stack
                command = MoveBoxCommand(box_id, old_pos, pos, self)
                self.controller.undo_stack.push(command)

    def on_box_item_resized(self, box_id: str, pos: QPointF, size: QPointF) -> None:
        if self.controller:
            logger.debug(
                f"Page box item {box_id} resized by relative position {pos} and size {size}"
            )
            ocr_box = self.controller.page.layout.get_ocr_box_by_id(box_id)
            if ocr_box:
                box_item = self.boxes[box_id]

                new_x = int(box_item.pos().x() + pos.x())
                new_y = int(box_item.pos().y() + pos.y())
                new_width = int(size.x())
                new_height = int(size.y())

                ocr_box.update_position(new_x, new_y, "GUI")
                ocr_box.update_size(new_width, new_height, "GUI")

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        if not self.controller:
            return

        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if item and isinstance(item, BoxItem):
            # Manually select the item under the cursor if it's not already selected
            if not item.isSelected():
                item.setSelected(True)

        selected_items = self.get_selected_box_items()
        if self.controller:
            self.controller.show_context_menu(selected_items)
        super().contextMenuEvent(event)

    def get_all_box_items(self) -> List[BoxItem]:
        return [item for item in self.items() if isinstance(item, BoxItem)]

    def get_selected_box_items(self) -> List[BoxItem]:
        return [item for item in self.selectedItems() if isinstance(item, BoxItem)]

    def get_box_under_cursor(self) -> Optional[BoxItem]:
        pos = self.views()[0].mapFromGlobal(QCursor.pos())
        item = self.itemAt(pos, self.views()[0].transform())
        if isinstance(item, BoxItem):
            return item
        return None

    def set_page_image(self, page_pixmap: QPixmap) -> None:
        if self.page_image_item:
            self.removeItem(self.page_image_item)

        self.page_image_item = QGraphicsPixmapItem(page_pixmap)
        self.page_image_item.setZValue(-1)
        self.page_image_item.setCacheMode(
            QGraphicsPixmapItem.CacheMode.DeviceCoordinateCache
        )
        self.page_image_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self.addItem(self.page_image_item)

    def add_header_footer(self, type: HEADER_FOOTER_ITEM_TYPE, y: float):
        if type is HEADER_FOOTER_ITEM_TYPE.HEADER:
            if self.header_item:
                self.removeItem(self.header_item)
        else:
            if self.footer_item:
                self.removeItem(self.footer_item)

        page_size = QSizeF(self.width(), self.height())
        item = HeaderFooterItem(type, page_size, y)
        self.addItem(item)
        item.setFocus()
        item.update_title()

        if type is HEADER_FOOTER_ITEM_TYPE.HEADER:
            self.header_item = item
        else:
            self.footer_item = item

    def update_header_footer(self, type: HEADER_FOOTER_ITEM_TYPE, y: float):
        if not self.controller:
            return

        if type is HEADER_FOOTER_ITEM_TYPE.HEADER and self.header_item:
            self.header_item.update_bottom_position(y)
            self.controller.set_header(int(y))
        elif type is HEADER_FOOTER_ITEM_TYPE.FOOTER and self.footer_item:
            self.footer_item.update_top_position(y)
            self.controller.set_footer(int(y))

    def drawForeground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        super().drawForeground(painter, rect)
        self.draw_box_flow_lines(painter)

    def draw_box_flow_lines(self, painter: QPainter):
        if not self.controller:
            return

        box_flow_line_color = self.application_settings.get(
            "box_flow_line_color", Qt.GlobalColor.black
        )

        pen = QPen(QColor(box_flow_line_color), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        color = pen.color()
        color.setAlpha(self.application_settings.get("box_flow_line_alpha", 128))
        pen.setColor(color)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        box_items = self.get_all_box_items()
        for box_item in box_items:
            ocr_box = self.controller.page.layout.get_ocr_box_by_id(box_item.box_id)
            if isinstance(ocr_box, TextBox) and ocr_box.flows_into_next:
                next_box_item = self.find_next_box_item(ocr_box)
                if next_box_item:
                    self.draw_box_flow_line(painter, box_item, next_box_item)

    def find_next_box_item(self, ocr_box: TextBox) -> Optional[BoxItem]:
        if not self.controller:
            return None

        next_box_order = ocr_box.order + 1
        for box in self.controller.page.layout.ocr_boxes:
            if box.order == next_box_order:
                next_box = self.controller.page.layout.get_ocr_box_by_id(box.id)
                if next_box:
                    return self.boxes.get(next_box.id)
        return None

    def draw_box_flow_line(
        self, painter: QPainter, start_box: BoxItem, end_box: BoxItem
    ):
        start_pos = start_box.sceneBoundingRect().bottomRight()
        end_pos = end_box.sceneBoundingRect().topLeft()
        painter.drawLine(start_pos, end_pos)

        # Draw arrowhead
        arrow_size = 10
        angle = math.atan2(end_pos.y() - start_pos.y(), end_pos.x() - start_pos.x())
        arrow_p1 = end_pos - QPointF(
            math.cos(angle - math.pi / 6) * arrow_size,
            math.sin(angle - math.pi / 6) * arrow_size,
        )
        arrow_p2 = end_pos - QPointF(
            math.cos(angle + math.pi / 6) * arrow_size,
            math.sin(angle + math.pi / 6) * arrow_size,
        )
        painter.drawPolygon([end_pos, arrow_p1, arrow_p2])

    def get_box_item_index_by_id(self, box_id: str) -> Optional[int]:
        for index, box_item in enumerate(self.get_all_box_items()):
            if box_item.box_id == box_id:
                return index
        return None

    def clear_box_items(self) -> None:
        for box_item in self.get_all_box_items():
            self.removeItem(box_item)
        self.boxes = {}
