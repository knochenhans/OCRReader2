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

    def setup_menus(self, actions):
        self.file_menu.addAction(actions.load_image_action)
        self.file_menu.addAction(actions.import_pdf_action)
        self.file_menu.addAction(actions.open_project_action)
        self.file_menu.addAction(actions.save_project_action)
        self.file_menu.addAction(actions.close_project_action)
        self.file_menu.addAction(actions.project_manager_action)
        self.file_menu.addAction(actions.export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(actions.exit_action)

        self.edit_menu.addAction(actions.settings_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.undo_action)
        self.edit_menu.addAction(actions.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.set_header_footer_for_project_action)
