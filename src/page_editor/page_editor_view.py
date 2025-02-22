from enum import Enum, auto
from typing import Optional
from PySide6.QtWidgets import QGraphicsView, QGraphicsRectItem
from PySide6.QtGui import QPainter, QMouseEvent, QEnterEvent, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF, QPoint

from page.page import Page  # type: ignore
from page_editor.page_editor_scene import PageEditorScene  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page_editor.box_item import BoxItem  # type: ignore

from loguru import logger

from page_editor.header_footer_item import HEADER_FOOTER_ITEM_TYPE  # type: ignore


class PageEditorViewState(Enum):
    DEFAULT = auto()
    SELECTING = auto()
    PANNING = auto()
    ZOOMING = auto()
    PLACE_HEADER = auto()
    PLACE_FOOTER = auto()


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
                self.enable_box_movement(True)
            case PageEditorViewState.SELECTING:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            case PageEditorViewState.PANNING:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                self.enable_box_movement(False)
            case PageEditorViewState.ZOOMING:
                self.viewport().setCursor(Qt.CursorShape.SizeVerCursor)
                self.enable_box_movement(False)
            case PageEditorViewState.PLACE_HEADER | PageEditorViewState.PLACE_FOOTER:
                self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
                self.enable_box_movement(False)

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
        if (
            event.key() == Qt.Key.Key_Plus
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            if self.current_zoom < self.max_zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.current_zoom += 1
        elif (
            event.key() == Qt.Key.Key_Minus
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            if self.current_zoom > self.min_zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.current_zoom -= 1
        elif (
            event.key() == Qt.Key.Key_0
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.resetTransform()
            self.current_zoom = 0
        elif event.key() == Qt.Key.Key_I:
            # Print information about the selected box
            selected_items = self.page_editor_scene.selectedItems()

            if selected_items:
                for item in selected_items:
                    if isinstance(item, BoxItem):
                        logger.info(f"Selected box: {item.box_id}")
                        logger.info(f"Position: {item.pos()}")
                        logger.info(f"Size: {item.rect()}")
        elif event.key() == Qt.Key.Key_Delete:
            # Delete selected boxes
            selected_items = self.page_editor_scene.selectedItems()

            if selected_items:
                for item in selected_items:
                    if isinstance(item, BoxItem):
                        if self.page_editor_scene.controller:
                            self.page_editor_scene.controller.remove_box(item.box_id)
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def enable_box_movement(self, enable: bool):
        for item in self.page_editor_scene.items():
            if isinstance(item, BoxItem):
                item.set_movable(enable)

    def check_box_position(self, pos: QPoint) -> bool:
        items = self.items(pos)
        for item in items:
            if isinstance(item, BoxItem):
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.show_context_menu([item.box_id])
                return True
        return False

    def get_mouse_position(self) -> QPointF:
        mouse_origin = self.mapFromGlobal(QCursor.pos())
        return self.mapToScene(mouse_origin)

    def set_header(self):
        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.HEADER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_HEADER)

    def set_footer(self):
        self.page_editor_scene.add_header_footer(
            HEADER_FOOTER_ITEM_TYPE.FOOTER,
            self.get_mouse_position().y(),
        )
        self.set_state(PageEditorViewState.PLACE_FOOTER)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
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
                    self.selection_rect.setRect(QRectF(event.pos(), event.pos()))
                    self.page_editor_scene.addItem(self.selection_rect)
        elif event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton
            and event.modifiers() & Qt.KeyboardModifier.NoModifier
        ):
            self.set_state(PageEditorViewState.PANNING)
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_state(PageEditorViewState.ZOOMING)
            self.last_mouse_position = event.pos().toPointF()

            # Check if the right click was on a box
            if not self.check_box_position(event.pos()):
                if self.page_editor_scene.controller:
                    self.page_editor_scene.controller.show_context_menu()
        # super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
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
        elif event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton
            and event.modifiers() & Qt.KeyboardModifier.NoModifier
        ):
            self.set_state(PageEditorViewState.DEFAULT)
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_state(PageEditorViewState.DEFAULT)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self.state == PageEditorViewState.PLACE_HEADER
            or self.state == PageEditorViewState.PLACE_FOOTER
        ):
            self.page_editor_scene.update_header_footer(event.pos().y())
            self.viewport().setCursor(Qt.CursorShape.SplitVCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
