from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import QSize

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Toolbar", parent)
        self.setIconSize(QSize(32, 32))

    def setup_toolbar(self, actions):
        self.addAction(actions.load_image_action)
        self.addAction(actions.open_project_action)
        self.addAction(actions.save_project_action)
        self.addAction(actions.export_action)
        self.addAction(actions.analyze_layout_action)
        self.addAction(actions.analyze_layout_and_recognize_action)
        self.addAction(actions.undo_action)
        self.addAction(actions.redo_action)