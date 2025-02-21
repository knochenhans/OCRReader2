from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import QWidget


class Actions:
    def __init__(self, parent, theme_folder: str, icon_path: str) -> None:
        self.parent = parent
        self.theme_folder: str = theme_folder
        self.icon_path: str = icon_path
        self.create_actions()

    def create_actions(self) -> None:
        # Exit action
        self.exit_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "close-circle-line.png")),
            QCoreApplication.translate("action_exit", "&Exit"),
            self.parent,
        )
        self.exit_action.setStatusTip(
            QCoreApplication.translate("status_exit", "Exit OCR Reader")
        )
        self.exit_action.triggered.connect(self.parent.close)
        self.exit_action.setShortcut(QKeySequence("Ctrl+q"))

        # Open project action
        self.open_project_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "folder-4-line.png")),
            QCoreApplication.translate("action_open_project", "&Open Project"),
            self.parent,
        )
        self.open_project_action.setStatusTip(
            QCoreApplication.translate("status_open_project", "Open Project")
        )
        self.open_project_action.setShortcut(QKeySequence("Ctrl+o"))
        self.open_project_action.triggered.connect(
            self.parent.user_actions.open_project
        )

        # Export project action
        self.export_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "folder-transfer-line.png")),
            QCoreApplication.translate("action_export_project", "&Export Project"),
            self.parent,
        )
        self.export_action.setStatusTip(
            QCoreApplication.translate("status_export_project", "Export Project")
        )
        self.export_action.setShortcut(QKeySequence("Ctrl+e"))
        self.export_action.triggered.connect(self.parent.user_actions.export_project)

        # Save project action
        self.save_project_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "save-line.png")),
            QCoreApplication.translate("action_save_project", "&Save Project"),
            self.parent,
        )
        self.save_project_action.setStatusTip(
            QCoreApplication.translate("status_save_project", "Save Project")
        )
        self.save_project_action.setShortcut(QKeySequence("Ctrl+s"))
        self.save_project_action.triggered.connect(
            self.parent.user_actions.save_project
        )

        # Load image action
        self.load_image_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "image-line.png")),
            QCoreApplication.translate("action_load_image", "&Load Image or PDF"),
            self.parent,
        )
        self.load_image_action.setStatusTip(
            QCoreApplication.translate("status_load_image", "Load Image")
        )
        self.load_image_action.setShortcut(QKeySequence("Ctrl+i"))
        self.load_image_action.triggered.connect(self.parent.user_actions.load_images)

        # Analyze layout action
        self.analyze_layout_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "layout-line.png")),
            QCoreApplication.translate("action_analyze_layout", "&Analyze Layout"),
            self.parent,
        )
        self.analyze_layout_action.setStatusTip(
            QCoreApplication.translate("status_analyze_layout", "Analyze Layout")
        )
        self.analyze_layout_action.setShortcut(QKeySequence("Ctrl+Alt+a"))
        self.analyze_layout_action.triggered.connect(
            self.parent.user_actions.analyze_layout
        )

        # Recognize OCR action
        self.recognize_ocr_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "ocr-line.png")),
            QCoreApplication.translate("action_recognize_ocr", "&Recognize OCR"),
            self.parent,
        )
        self.recognize_ocr_action.setStatusTip(
            QCoreApplication.translate("status_recognize_ocr", "Recognize OCR")
        )
        self.recognize_ocr_action.setShortcut(QKeySequence("Ctrl+Alt+o"))
        self.recognize_ocr_action.triggered.connect(
            self.parent.user_actions.recognize_boxes
        )

        # Analyze layout and recognize action
        self.analyze_layout_and_recognize_action: QAction = QAction(
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
        self.analyze_layout_and_recognize_action.triggered.connect(
            self.parent.user_actions.analyze_layout_and_recognize
        )

        # Remove line breaks action
        self.remove_line_breaks_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "text-wrap-line.png")),
            QCoreApplication.translate(
                "action_remove_line_breaks", "Remove Line Breaks"
            ),
            self.parent,
        )
        self.remove_line_breaks_action.setStatusTip(
            QCoreApplication.translate(
                "status_remove_line_breaks", "Remove Line Breaks"
            )
        )
        self.remove_line_breaks_action.setShortcut(QKeySequence("Ctrl+Alt+l"))
        self.remove_line_breaks_action.triggered.connect(
            self.parent.user_actions.remove_line_breaks
        )

        # Close project action
        self.close_project_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "close-line.png")),
            QCoreApplication.translate("action_close_project", "&Close project"),
            self.parent,
        )
        self.close_project_action.setStatusTip(
            QCoreApplication.translate("status_close_project", "Close project")
        )
        self.close_project_action.setShortcut(QKeySequence("Ctrl+w"))

        # Undo action
        self.undo_action: QAction = self.parent.undo_stack.createUndoAction(
            self.parent, QCoreApplication.translate("Undo", "&Undo")
        )
        self.undo_action.setIcon(
            QIcon(self.icon_path.format(self.theme_folder, "arrow-go-back-line.png"))
        )
        self.undo_action.setShortcut(QKeySequence("Ctrl+z"))

        # Redo action
        self.redo_action: QAction = self.parent.undo_stack.createRedoAction(
            self.parent, QCoreApplication.translate("Redo", "&Redo")
        )
        self.redo_action.setIcon(
            QIcon(self.icon_path.format(self.theme_folder, "arrow-go-forward-line.png"))
        )
        self.redo_action.setShortcut(QKeySequence("Ctrl+y"))

        # Preferences action
        self.preferences_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "settings-3-line.png")),
            QCoreApplication.translate("action_preferences", "&Preferences"),
            self.parent,
        )
        self.preferences_action.setStatusTip(
            QCoreApplication.translate("status_preferences", "Preferences")
        )
        self.preferences_action.setShortcut(QKeySequence("Ctrl+p"))

        # Delete selected pages action
        self.delete_selected_pages_action: QAction = QAction(
            QCoreApplication.translate("delete_pages", "Delete"), self.parent
        )
        self.delete_selected_pages_action.setShortcut(QKeySequence("Delete"))

        # Project manager action
        self.project_manager_action: QAction = QAction(
            QIcon(self.icon_path.format(self.theme_folder, "folder-line.png")),
            QCoreApplication.translate("action_project_manager", "&Project Manager"),
            self.parent,
        )
        self.project_manager_action.setStatusTip(
            QCoreApplication.translate("status_project_manager", "Project Manager")
        )
        self.project_manager_action.setShortcut(QKeySequence("Ctrl+Shift+p"))
        self.project_manager_action.triggered.connect(
            self.parent.project_manager_window.show
        )
