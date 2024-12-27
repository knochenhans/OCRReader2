from page.page import Page  # type: ignore

from PySide6.QtGui import QPixmap


class PageEditorController:
    def __init__(self, page: Page, scene):
        self.page = page
        self.scene = scene

    def set_page_image(self, image_path):
        self.page.image_path = image_path
        self.scene.set_page_image(QPixmap(image_path))
