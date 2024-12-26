from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, QAction, QKeySequence


class Actions:
    def __init__(self, parent, theme_folder, icon_path):
        self.parent = parent
        self.theme_folder = theme_folder
        self.icon_path = icon_path
        self.create_actions()

    def create_actions(self):
        self.exit_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "close-circle-line.png")),
            QCoreApplication.translate("action_exit", "&Exit"),
            self.parent,
        )
        self.exit_action.setStatusTip(
            QCoreApplication.translate("status_exit", "Exit OCR Reader")
        )
        self.exit_action.triggered.connect(self.parent.close)
        self.exit_action.setShortcut(QKeySequence("Ctrl+q"))

        self.open_project_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "folder-4-line.png")),
            QCoreApplication.translate("action_open_project", "&Open Project"),
            self.parent,
        )
        self.open_project_action.setStatusTip(
            QCoreApplication.translate("status_open_project", "Open Project")
        )
        self.open_project_action.setShortcut(QKeySequence("Ctrl+o"))

        self.export_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "folder-transfer-line.png")),
            QCoreApplication.translate("action_export_project", "&Export Project"),
            self.parent,
        )
        self.export_action.setStatusTip(
            QCoreApplication.translate("status_export_project", "Export Project")
        )
        self.export_action.setShortcut(QKeySequence("Ctrl+e"))

        self.save_project_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "save-line.png")),
            QCoreApplication.translate("action_save_project", "&Save Project"),
            self.parent,
        )
        self.save_project_action.setStatusTip(
            QCoreApplication.translate("status_save_project", "Save Project")
        )
        self.save_project_action.setShortcut(QKeySequence("Ctrl+s"))

        self.load_image_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "image-line.png")),
            QCoreApplication.translate("action_load_image", "&Load Image or PDF"),
            self.parent,
        )
        self.load_image_action.setStatusTip(
            QCoreApplication.translate("status_load_image", "Load Image")
        )
        self.load_image_action.setShortcut(QKeySequence("Ctrl+i"))

        self.analyze_layout_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "layout-line.png")),
            QCoreApplication.translate("action_analyze_layout", "&Analyze Layout"),
            self.parent,
        )
        self.analyze_layout_action.setStatusTip(
            QCoreApplication.translate("status_analyze_layout", "Analyze Layout")
        )
        self.analyze_layout_action.setShortcut(QKeySequence("Ctrl+Alt+a"))

        self.analyze_layout_and_recognize_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "layout-fill.png")),
            QCoreApplication.translate(
                "action_analyze_layout_and_recognize", "Analyze Layout and &Recognize"
            ),
            self.parent,
        )
        self.analyze_layout_and_recognize_action.setStatusTip(
            QCoreApplication.translate(
                "status_analyze_layout_and_recognize", "Analyze Layout and Recognize"
            )
        )
        self.analyze_layout_and_recognize_action.setShortcut(QKeySequence("Ctrl+Alt+r"))

        self.close_project_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "close-line.png")),
            QCoreApplication.translate("action_close_project", "&Close project"),
            self.parent,
        )
        self.close_project_action.setStatusTip(
            QCoreApplication.translate("status_close_project", "Close project")
        )
        self.close_project_action.setShortcut(QKeySequence("Ctrl+w"))

        self.undo_action = self.parent.undo_stack.createUndoAction(
            self.parent, QCoreApplication.translate("Undo", "&Undo")
        )
        self.undo_action.setIcon(
            QIcon(self.icon_path.format(self.theme_folder, "arrow-go-back-line.png"))
        )
        self.undo_action.setShortcut(QKeySequence("Ctrl+z"))

        self.redo_action = self.parent.undo_stack.createRedoAction(
            self.parent, QCoreApplication.translate("Redo", "&Redo")
        )
        self.redo_action.setIcon(
            QIcon(self.icon_path.format(self.theme_folder, "arrow-go-forward-line.png"))
        )
        self.redo_action.setShortcut(QKeySequence("Ctrl+y"))

        self.preferences_action = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "settings-3-line.png")),
            QCoreApplication.translate("action_preferences", "&Preferences"),
            self.parent,
        )
        self.preferences_action.setStatusTip(
            QCoreApplication.translate("status_preferences", "Preferences")
        )
        self.preferences_action.setShortcut(QKeySequence("Ctrl+p"))

        self.delete_selected_pages_action = QAction(
            QCoreApplication.translate("delete_pages", "Delete"), self.parent
        )
        self.delete_selected_pages_action.setShortcut(QKeySequence("Delete"))

        # self.page_icon_view_context_menu.addAction(self.load_image_action)
