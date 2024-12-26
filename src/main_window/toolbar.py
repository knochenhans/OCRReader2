from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import QSize

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Toolbar", parent)
        self.setIconSize(QSize(32, 32))
        self.setup_toolbar()

    def setup_toolbar(self):
        self.toolbar = QToolBar("Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))