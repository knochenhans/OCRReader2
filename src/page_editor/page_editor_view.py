from typing import Optional
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter, QImage, QPixmap, QMouseEvent, QEnterEvent
from PySide6.QtCore import Qt, QEvent


from page.page import Page  # type: ignore
from page_editor.page_editor_scene import PageEditorScene  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from page.box_type import BoxType  # type: ignore


class PageEditorView(QGraphicsView):
    def __init__(self, page: Page) -> None:
        super().__init__()
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setInteractive(True)
        self.last_mouse_position = None

        self.zoom_factor = 1.02
        self.current_zoom = 0
        self.max_zoom = 100
        self.min_zoom = -100
        self.accumulated_delta = 0

        self.page_editor_scene = PageEditorScene()
        controller = PageEditorController(page, self.page_editor_scene)

        self.page_editor_scene.controller = controller

        self.setScene(self.page_editor_scene)

        self.setMouseTracking(True)

        self.resize(1280, 1024)

        for box in page.layout.boxes:
            if box.type in [
                BoxType.FLOWING_TEXT,
                BoxType.CAPTION_TEXT,
                BoxType.HEADING_TEXT,
            ]:
                self.page_editor_scene.add_box(box)

        image = QImage(page.image_path)
        self.page_editor_scene.set_page_image(QPixmap.fromImage(image))

    def set_page(self, page: Page) -> None:
        # self.page_editor_scene.set_page(page)
        # self.page_editor_scene.update()
        pass

    def wheelEvent(self, event):
        self.accumulated_delta += event.angleDelta().y()

        # Only apply zoom for significant accumulated deltas (e.g., 120 is one tick on most systems)
        while abs(self.accumulated_delta) >= 120:
            if self.accumulated_delta > 0:
                # Zoom in
                if self.current_zoom < self.max_zoom:
                    scale_factor = self.calculate_acceleration_factor()
                    self.scale(scale_factor, scale_factor)
                    self.current_zoom += 1
                    self.accumulated_delta -= 120
            else:
                # Zoom out
                if self.current_zoom > self.min_zoom:
                    scale_factor = self.calculate_acceleration_factor()
                    self.scale(1 / scale_factor, 1 / scale_factor)
                    self.current_zoom -= 1
                    self.accumulated_delta += 120

    def calculate_acceleration_factor(self):
        # Higher accumulated delta leads to a larger zoom factor
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
            # Ctrl + Plus: Zoom In
            if self.current_zoom < self.max_zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.current_zoom += 1
        elif (
            event.key() == Qt.Key.Key_Minus
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl + Minus: Zoom Out
            if self.current_zoom > self.min_zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.current_zoom -= 1
        elif (
            event.key() == Qt.Key.Key_0
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl + 0: Reset Zoom
            self.resetTransform()
            self.current_zoom = 0
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
