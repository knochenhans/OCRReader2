import weakref
from enum import Enum, auto
from typing import Callable, List, Optional

from loguru import logger
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, Signal, Slot
from PySide6.QtGui import (
    QCursor,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPainter,
)
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsView

from main_window.page_actions import PageActions  # type: ignore
from page.box_type import BoxType  # type: ignore
from page.page import Page  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore
from page_editor.header_footer_item import HEADER_FOOTER_ITEM_TYPE  # type: ignore
from page_editor.ocr_actions import OCRActions  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page_editor.page_editor_scene import PageEditorScene  # type: ignore
from settings.settings import Settings  # type: ignore


class PageEditorViewState(Enum):
    DEFAULT = auto()
    SELECTING = auto()
    PANNING = auto()
    ZOOMING = auto()
    PLACE_HEADER = auto()
    PLACE_FOOTER = auto()
    PLACE_BOX = auto()
    PLACE_RECOGNITION_BOX = auto()
    SET_BOX_FLOW = auto()
    SET_BOX_SPLIT = auto()


class PageEditorView(QGraphicsView):
    box_selection_changed = Signal(list)
    edit_state_changed = Signal(str)

    def __init__(
        self,
        application_settings: Settings,
        project_settings: Optional[Settings] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> None:
        super().__init__()

        self.application_settings = application_settings
        self.project_settings = project_settings
        self.progress_callback = progress_callback

        self.page_actions: Optional[PageActions] = None
        self.ocr_actions: Optional[OCRActions] = None

        self.page_editor_scene: Optional[PageEditorScene] = None

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
        self.current_zoom = 0.0
        self.max_zoom = 100
        self.min_zoom = -100
        self.accumulated_delta = 0

        self.setMouseTracking(True)

        self.selection_rect = None

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.state = PageEditorViewState.DEFAULT

        self.box_flow_selection: List[BoxItem] = []

        self.custom_shortcuts: dict = {}

    def clear_page(self) -> None:
        if self.page_editor_scene:
            if self.page_editor_scene.controller:
                self.page_editor_scene.controller.clear_boxes_callbacks()
            self.page_editor_scene.selectionChanged.disconnect(
                self.on_box_selection_changed
            )
            self.page_editor_scene.deleteLater()
            self.page_editor_scene = None
        self.viewport().hide()

    def set_page(self, page: Page) -> None:
        self.clear_page()
        self.viewport().show()

        self.page_editor_scene = PageEditorScene(self.application_settings)
        controller = PageEditorController(
            page,
            self.page_editor_scene,
            self.application_settings,
            self.project_settings,
            self.progress_callback,
        )
        self.page_editor_scene.controller = weakref.proxy(controller)
        self.setScene(self.page_editor_scene)
        self.page_editor_scene.controller.open_page()
        self.page_editor_scene.selectionChanged.connect(self.on_box_selection_changed)
        self.viewport().setFocus()

    @Slot()
    def on_box_selection_changed(self) -> None:
        if not self.page_editor_scene:
            return

        if not self.page_editor_scene.controller:
            return

        box_items = self.page_editor_scene.get_selected_box_items()

        box_ids = [box.box_id for box in box_items]

        ocr_boxes = [
            self.page_editor_scene.controller.page.layout.get_ocr_box_by_id(box_id)
            for box_id in box_ids
        ]

        self.box_selection_changed.emit(ocr_boxes)

    def set_state(self, state: PageEditorViewState) -> None:
        self.state = state
        match state:
            case PageEditorViewState.DEFAULT:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.enable_boxes(True)
                self.box_flow_selection = []
                self.edit_state_changed.emit("Default")
            case PageEditorViewState.SELECTING:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.enable_boxes(True)
                # self.edit_state_changed.emit("Selecting")
            case PageEditorViewState.PANNING:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                self.enable_boxes(False)
                # self.edit_state_changed.emit("Panning")
            case PageEditorViewState.ZOOMING:
                self.viewport().setCursor(Qt.CursorShape.SizeVerCursor)
                self.enable_boxes(False)
                # self.edit_state_changed.emit("Zooming")
            case PageEditorViewState.PLACE_HEADER:
                self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Placing Header")
            case PageEditorViewState.PLACE_FOOTER:
                self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Placing Footer")
            case PageEditorViewState.PLACE_BOX:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Placing Box")
            case PageEditorViewState.PLACE_RECOGNITION_BOX:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Placing Recognition Box")
            case PageEditorViewState.SET_BOX_FLOW:
                self.box_flow_count = 0
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Setting Box Flow")
            case PageEditorViewState.SET_BOX_SPLIT:
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
                self.enable_boxes(False)
                self.edit_state_changed.emit("Setting Box Split")

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
        if not self.page_editor_scene:
            return

        self.fitInView(
            self.page_editor_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def handle_global_key_event(self, event: QKeyEvent):
        pass

    def keyPressEvent(self, event):
        if not self.page_editor_scene:
            return

        match event.key():
            case Qt.Key.Key_Plus if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.current_zoom < self.max_zoom:
                    self.scale(self.zoom_factor, self.zoom_factor)
                    self.current_zoom += 1
            case Qt.Key.Key_Minus if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.current_zoom > self.min_zoom:
                    self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                    self.current_zoom -= 1
            case Qt.Key.Key_0 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
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
            case Qt.Key.Key_R if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.renumber_box()
            case Qt.Key.Key_A:
                self.start_place_box()
            case Qt.Key.Key_R:
                self.start_place_recognition_box()
            case Qt.Key.Key_F1:
                if self.ocr_actions:
                    self.ocr_actions.analyze_layout()
            case Qt.Key.Key_F2:
                if self.ocr_actions:
                    self.ocr_actions.recognize_boxes()
            case Qt.Key.Key_F3:
                self.start_box_flow_selection()
            case Qt.Key.Key_F5:
                if self.page_actions:
                    self.page_actions.ocr_editor()
            case Qt.Key.Key_F6:
                if self.page_actions:
                    self.page_actions.ocr_editor_project()
            case Qt.Key.Key_B:
                self.toggle_box_flow()
            case Qt.Key.Key_M:
                self.merge_selected_boxes()
            case Qt.Key.Key_S:
                self.start_box_split()
            case Qt.Key.Key_Z if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.undo_stack.undo()
            case Qt.Key.Key_Y if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.undo_stack.redo()
            case Qt.Key.Key_PageUp:
                if self.page_actions:
                    self.page_actions.previous_page()
            case Qt.Key.Key_PageDown:
                if self.page_actions:
                    self.page_actions.next_page()
            case Qt.Key.Key_1 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 1")
            case Qt.Key.Key_2 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 2")
            case Qt.Key.Key_3 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 3")
            case Qt.Key.Key_4 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 4")
            case Qt.Key.Key_5 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 5")
            case Qt.Key.Key_6 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 6")
            case Qt.Key.Key_7 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 7")
            case Qt.Key.Key_8 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 8")
            case Qt.Key.Key_9 if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.change_selected_boxes_type("Alt + 9")
            case Qt.Key.Key_1 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 1")
            case Qt.Key.Key_2 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 2")
            case Qt.Key.Key_3 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 3")
            case Qt.Key.Key_4 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 4")
            case Qt.Key.Key_5 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 5")
            case Qt.Key.Key_6 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 6")
            case Qt.Key.Key_7 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 7")
            case Qt.Key.Key_8 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 8")
            case Qt.Key.Key_9 if (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.set_custom_user_tag("Ctrl + 9")
            case Qt.Key.Key_Escape:
                self.set_state(PageEditorViewState.DEFAULT)
            case _ if event.matches(QKeySequence.StandardKey.SelectAll):
                # Select all boxes
                for item in self.page_editor_scene.items():
                    if isinstance(item, BoxItem):
                        item.setSelected(True)
            case _:
                super().keyPressEvent(event)

    def set_zoom(self, zoom: float) -> None:
        if not self.page_editor_scene:
            return

        current_zoom = self.current_zoom
        if zoom > current_zoom:
            while self.current_zoom < zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.current_zoom += 1
        elif zoom < current_zoom:
            while self.current_zoom > zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.current_zoom -= 1
        self.current_zoom = zoom

    def change_selected_boxes_type(self, key: str):
        box_type_str = self.custom_shortcuts.get(key, None)
        if not box_type_str:
            return

        box_type = BoxType[box_type_str]

        if not self.page_editor_scene:
            return

        if self.page_editor_scene.controller:
            self.page_editor_scene.controller.change_box_type_for_selected_boxes(
                box_type
            )

    def set_custom_user_tag(self, key: str):
        if not self.page_editor_scene:
            return

        value = self.custom_shortcuts.get(key, "")

        if value == "":
            return

        selected_items = self.page_editor_scene.selectedItems()
        if selected_items:
            for item in selected_items:
                if isinstance(item, BoxItem):
                    if self.page_editor_scene.controller:
                        self.page_editor_scene.controller.add_custom_user_data(
                            item.box_id, "class", value
                        )

    def focusNextChild(self) -> bool:
        if not self.page_editor_scene:
            return super().focusNextChild()

        self.page_editor_scene.select_next_box()
        return super().focusNextChild()

    def enable_boxes(self, enable: bool) -> None:
        if not self.page_editor_scene:
            return

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
        if not self.page_editor_scene:
            return

        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.HEADER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_HEADER)

    def start_place_footer(self) -> None:
        if not self.page_editor_scene:
            return

        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.FOOTER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_FOOTER)

    def start_place_box(self):
        self.set_state(PageEditorViewState.PLACE_BOX)

    def start_place_recognition_box(self):
        self.set_state(PageEditorViewState.PLACE_RECOGNITION_BOX)

    def start_box_flow_selection(self):
        self.set_state(PageEditorViewState.SET_BOX_FLOW)

    def start_box_split(self):
        self.set_state(PageEditorViewState.SET_BOX_SPLIT)

    def toggle_box_flow(self):
        if not self.page_editor_scene:
            return

        if self.page_editor_scene.controller:
            self.page_editor_scene.controller.toggle_box_flow()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.page_editor_scene:
            return

        match self.state:
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.set_state(PageEditorViewState.DEFAULT)
                return
            case (
                PageEditorViewState.PLACE_BOX
                | PageEditorViewState.PLACE_RECOGNITION_BOX
            ):
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
            case PageEditorViewState.SET_BOX_SPLIT:
                box_item = self.check_box_position(event.pos())

                if box_item:
                    if self.page_editor_scene.controller:
                        mapped_pos = self.mapToScene(event.pos())
                        self.page_editor_scene.controller.split_y_ocr_box(
                            box_item.box_id, int(mapped_pos.y())
                        )

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
                case Qt.MouseButton.MiddleButton | Qt.MouseButton.LeftButton if (
                    event.modifiers() & Qt.KeyboardModifier.NoModifier
                ):
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
        if not self.page_editor_scene:
            return

        match self.state:
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.set_state(PageEditorViewState.DEFAULT)
                return
            case PageEditorViewState.PLACE_BOX:
                rect = self.rubberBandRect()
                scene_rect = self.mapToScene(rect).boundingRect()
                order = -1
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.add_box(
                        (
                            int(scene_rect.x()),
                            int(scene_rect.y()),
                            int(scene_rect.width()),
                            int(scene_rect.height()),
                        ),
                        BoxType.FLOWING_TEXT,
                        order,
                    )
                self.set_state(PageEditorViewState.DEFAULT)
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
            case Qt.MouseButton.MiddleButton | Qt.MouseButton.LeftButton if (
                event.modifiers() & Qt.KeyboardModifier.NoModifier
            ):
                self.set_state(PageEditorViewState.DEFAULT)
            case Qt.MouseButton.RightButton:
                self.set_state(PageEditorViewState.DEFAULT)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.page_editor_scene:
            return

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

    def merge_selected_boxes(self):
        if not self.page_editor_scene:
            return

        if self.page_editor_scene.controller:
            self.page_editor_scene.controller.merge_selected_boxes()
