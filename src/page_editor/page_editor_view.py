from enum import Enum, auto
from typing import List, Optional
from PySide6.QtWidgets import QGraphicsView, QGraphicsRectItem
from PySide6.QtGui import QPainter, QMouseEvent, QCursor, QKeySequence
from PySide6.QtCore import Qt, QRectF, QPointF, QPoint

from page.box_type import BoxType  # type: ignore
from page.page import Page  # type: ignore
from page_editor.page_editor_scene import PageEditorScene  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore
from page_editor.header_footer_item import HEADER_FOOTER_ITEM_TYPE  # type: ignore

from loguru import logger


class PageEditorViewState(Enum):
    DEFAULT = auto()
    SELECTING = auto()
    PANNING = auto()
    ZOOMING = auto()
    PLACE_HEADER = auto()
    PLACE_FOOTER = auto()
    PLACE_RECOGNITION_BOX = auto()
    SET_BOX_FLOW = auto()


class PageEditorView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setInteractive(True)
        self.last_mouse_position = QPointF()

        self.zoom_factor = 1.02
        self.current_zoom = 0
        self.max_zoom = 100
        self.min_zoom = -100
        self.accumulated_delta = 0

        # self.set_page(page)

        self.setMouseTracking(True)

        # self.resize(1280, 1024)

        self.selection_rect = None

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.state = PageEditorViewState.DEFAULT

        self.box_flow_selection: List[BoxItem] = []

    def set_page(self, page: Page) -> None:
        self.page_editor_scene = PageEditorScene()
        controller = PageEditorController(page, self.page_editor_scene)
        self.page_editor_scene.controller = controller
        self.setScene(self.page_editor_scene)
        self.page_editor_scene.controller.open_page()

    def set_state(self, state: PageEditorViewState) -> None:
        self.state = state
        match state:
            case PageEditorViewState.DEFAULT:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.enable_boxes(True)
                self.box_flow_selection = []
            case PageEditorViewState.SELECTING:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.enable_boxes(True)
            case PageEditorViewState.PANNING:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                self.enable_boxes(False)
            case PageEditorViewState.ZOOMING:
                self.viewport().setCursor(Qt.CursorShape.SizeVerCursor)
                self.enable_boxes(False)
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
                self.enable_boxes(False)
            case PageEditorViewState.PLACE_RECOGNITION_BOX:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)
            case PageEditorViewState.SET_BOX_FLOW:
                self.box_flow_count = 0
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)

        logger.debug(f"Set state: {state.name}")

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.accumulated_delta += event.angleDelta().y()

            while abs(self.accumulated_delta) >= 120:
                if self.accumulated_delta > 0:
                    if self.current_zoom < self.max_zoom:
                        scale_factor = self.calculate_acceleration_factor()
                        self.scale(scale_factor, scale_factor)
                        self.current_zoom += 1
                        self.accumulated_delta -= 120
                else:
                    if self.current_zoom > self.min_zoom:
                        scale_factor = self.calculate_acceleration_factor()
                        self.scale(1 / scale_factor, 1 / scale_factor)
                        self.current_zoom -= 1
                        self.accumulated_delta += 120
        elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - event.angleDelta().y()
            )
        else:
            super().wheelEvent(event)

    def calculate_acceleration_factor(self):
        return self.zoom_factor + (abs(self.accumulated_delta) / 120 - 1) * 0.05

    def reset_zoom(self):
        self.resetTransform()
        self.current_zoom = 0

    def zoom_to_fit(self):
        self.fitInView(
            self.page_editor_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def keyPressEvent(self, event):
        match event.key():
            case (
                Qt.Key.Key_Plus
            ) if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if self.current_zoom < self.max_zoom:
                    self.scale(self.zoom_factor, self.zoom_factor)
                    self.current_zoom += 1
            case (
                Qt.Key.Key_Minus
            ) if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if self.current_zoom > self.min_zoom:
                    self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                    self.current_zoom -= 1
            case (
                Qt.Key.Key_0
            ) if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.resetTransform()
                self.current_zoom = 0
            case Qt.Key.Key_I:
                # Print information about the selected box
                selected_items = self.page_editor_scene.selectedItems()
                if selected_items:
                    for item in selected_items:
                        if isinstance(item, BoxItem):
                            logger.info(f"Selected box: {item.box_id}")
                            logger.info(f"Position: {item.pos()}")
                            logger.info(f"Size: {item.rect()}")
            case Qt.Key.Key_Delete:
                # Delete selected boxes
                selected_items = self.page_editor_scene.selectedItems()
                if selected_items:
                    for item in selected_items:
                        if isinstance(item, BoxItem):
                            if self.page_editor_scene.controller:
                                self.page_editor_scene.controller.remove_box(
                                    item.box_id
                                )
            case Qt.Key.Key_H:
                self.start_place_header()
            case Qt.Key.Key_F:
                self.start_place_footer()
            # case Qt.Key.Key_Tab:
            #     self.page_editor_scene.select_next_box()
            case Qt.Key.Key_R:
                self.start_place_recognition_box()
            case Qt.Key.Key_F2:
                self.start_box_flow_selection()
            case Qt.Key.Key_B:
                self.set_box_flow()
            case Qt.Key.Key_1 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type(BoxType.FLOWING_TEXT)
            case Qt.Key.Key_2 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type(BoxType.HEADING_TEXT)
            case Qt.Key.Key_Escape:
                self.set_state(PageEditorViewState.DEFAULT)
            case _ if event.matches(QKeySequence.StandardKey.SelectAll):
                # Select all boxes
                for item in self.page_editor_scene.items():
                    if isinstance(item, BoxItem):
                        item.setSelected(True)
            case _:
                super().keyPressEvent(event)

    def change_selected_boxes_type(self, box_type: BoxType):
        selected_items = self.page_editor_scene.selectedItems()
        if selected_items:
            for item in selected_items:
                if isinstance(item, BoxItem):
                    if self.page_editor_scene.controller:
                        self.page_editor_scene.controller.change_box_type(
                            item.box_id, box_type
                        )

    # def enterEvent(self, event: QEnterEvent) -> None:
    #     super().enterEvent(event)
    #     self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def focusNextChild(self) -> bool:
        self.page_editor_scene.select_next_box()
        return super().focusNextChild()

    def enable_boxes(self, enable: bool) -> None:
        for item in self.page_editor_scene.items():
            if isinstance(item, BoxItem):
                item.enable(enable)
                item.set_movable(enable)

    def check_box_position(self, pos: QPoint) -> Optional[BoxItem]:
        items = self.items(pos)
        for item in items:
            if isinstance(item, BoxItem):
                return item
        return None

    def get_mouse_position(self) -> QPointF:
        mouse_origin = self.mapFromGlobal(QCursor.pos())
        return self.mapToScene(mouse_origin)

    def start_place_header(self) -> None:
        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.HEADER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_HEADER)

    def start_place_footer(self) -> None:
        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.FOOTER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_FOOTER)

    def start_place_recognition_box(self):
        self.set_state(PageEditorViewState.PLACE_RECOGNITION_BOX)

    def start_box_flow_selection(self):
        self.set_state(PageEditorViewState.SET_BOX_FLOW)

    def set_box_flow(self):
        if self.page_editor_scene.controller:
            self.page_editor_scene.controller.toggle_box_flow()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        match self.state:
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.set_state(PageEditorViewState.DEFAULT)
                return
            case PageEditorViewState.PLACE_RECOGNITION_BOX:
                super().mousePressEvent(event)
                return
            case PageEditorViewState.SET_BOX_FLOW:
                box_item = self.check_box_position(event.pos())

                if box_item:
                    if self.page_editor_scene.controller:
                        if len(self.box_flow_selection) == 0:
                            self.box_flow_selection.append(box_item)
                        else:
                            self.box_flow_selection.append(box_item)
                            self.page_editor_scene.controller.toggle_box_flow(
                                self.box_flow_selection
                            )
                            self.set_state(PageEditorViewState.DEFAULT)

                super().mousePressEvent(event)
                return
        item = self.itemAt(event.pos())
        if item and isinstance(item, BoxItem):
            # Disable rubberband selection when moving or resizing items
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        else:
            match event.button():
                case Qt.MouseButton.LeftButton:
                    if (
                        event.modifiers() & Qt.KeyboardModifier.ControlModifier
                        and event.modifiers() & Qt.KeyboardModifier.AltModifier
                    ):
                        self.set_state(PageEditorViewState.PANNING)
                    else:
                        self.set_state(PageEditorViewState.SELECTING)
                        if self.selection_rect:
                            self.selection_rect = QGraphicsRectItem()
                            self.selection_rect.setPen(Qt.PenStyle.DashLine)
                            self.selection_rect.setBrush(Qt.GlobalColor.transparent)
                            self.selection_rect.setRect(
                                QRectF(event.pos(), event.pos())
                            )
                            self.page_editor_scene.addItem(self.selection_rect)
                    super().mousePressEvent(event)
                case (
                    Qt.MouseButton.MiddleButton | Qt.MouseButton.LeftButton
                ) if event.modifiers() & Qt.KeyboardModifier.NoModifier:
                    self.set_state(PageEditorViewState.PANNING)
                case Qt.MouseButton.RightButton:
                    # for item in self.page_editor_scene.selectedItems():
                    #     item.setSelected(False)

                    # box_item = self.check_box_position(event.pos())
                    # if box_item:
                    #     box_item.setSelected(True)
                    # else:
                    #     self.set_state(PageEditorViewState.DEFAULT)
                    pass
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        match self.state:
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.set_state(PageEditorViewState.DEFAULT)
                return
            case PageEditorViewState.PLACE_RECOGNITION_BOX:
                rect = self.rubberBandRect()
                scene_rect = self.mapToScene(rect).boundingRect()
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.analyze_region(
                        (
                            int(scene_rect.x()),
                            int(scene_rect.y()),
                            int(scene_rect.width()),
                            int(scene_rect.height()),
                        )
                    )
                self.set_state(PageEditorViewState.DEFAULT)
                return
            case PageEditorViewState.SET_BOX_FLOW:
                # self.set_state(PageEditorViewState.DEFAULT)
                return

        match event.button():
            case Qt.MouseButton.LeftButton:
                if (
                    event.modifiers() & Qt.KeyboardModifier.ControlModifier
                    and event.modifiers() & Qt.KeyboardModifier.AltModifier
                ):
                    self.set_state(PageEditorViewState.DEFAULT)
                else:
                    self.set_state(PageEditorViewState.DEFAULT)
                    if self.selection_rect:
                        self.page_editor_scene.removeItem(self.selection_rect)
                        self.selection_rect = None
            case (
                Qt.MouseButton.MiddleButton | Qt.MouseButton.LeftButton
            ) if event.modifiers() & Qt.KeyboardModifier.NoModifier:
                self.set_state(PageEditorViewState.DEFAULT)
            case Qt.MouseButton.RightButton:
                self.set_state(PageEditorViewState.DEFAULT)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self.state == PageEditorViewState.PLACE_HEADER
            or self.state == PageEditorViewState.PLACE_FOOTER
        ):
            scene_pos = self.mapToScene(event.pos())

            if self.state == PageEditorViewState.PLACE_HEADER:
                self.page_editor_scene.update_header_footer(
                    HEADER_FOOTER_ITEM_TYPE.HEADER, scene_pos.y()
                )
            else:
                self.page_editor_scene.update_header_footer(
                    HEADER_FOOTER_ITEM_TYPE.FOOTER, scene_pos.y()
                )
            self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
        else:
            # self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            super().mouseMoveEvent(event)
