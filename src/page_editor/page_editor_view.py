from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter

from page_editor.page_editor_scene import PageEditorScene # type: ignore
from page.page import Page # type: ignore
from page_editor.page_editor_controller import PageEditorController # type: ignore


class PageEditorView(QGraphicsView):
    def __init__(self, page: Page) -> None:
        super().__init__()

        # self.setRenderHint(QPainter.Antialiasing)
        # self.setRenderHint(QPainter.TextAntialiasing)
        # self.setRenderHint(QPainter.SmoothPixmapTransform)
        # self.setRenderHint(QPainter.HighQualityAntialiasing

        self.page_editor_scene = PageEditorScene()
        controller = PageEditorController(page, self.page_editor_scene)

        self.page_editor_scene.controller = controller

        self.setScene(self.page_editor_scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )

        self.setMouseTracking(True)

        self.resize(1280, 1024)

        for box in page.layout.boxes:
            self.page_editor_scene.add_box(box)

        image = QImage(page.image_path)
        self.page_editor_scene.set_page_image(QPixmap.fromImage(image))

    def set_page(self, page: Page) -> None:
        # self.page_editor_scene.set_page(page)
        # self.page_editor_scene.update()
        pass