from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMenuBar, QMenu


class Menus:
    def __init__(self, parent):
        self.menu_bar = QMenuBar(parent)
        self.file_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("menu_file", "&File")
        )
        self.edit_menu = self.menu_bar.addMenu(
            QCoreApplication.translate("menu_edit", "&Edit")
        )
        self.setup_menus()

    def setup_menus(self):
        # Add menu actions here
        pass
