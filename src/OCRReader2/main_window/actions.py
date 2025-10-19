from typing import Any, Dict

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QWidget


class Actions:
    def __init__(self, parent: QWidget, theme_folder: str, icon_path: str) -> None:
        self.parent = parent
        self.theme_folder: str = theme_folder
        self.icon_path: str = icon_path
        self.create_actions()

    def create_actions(self) -> None:
        actions_info: Dict[str, Any] = {
            "exit_action": {
                "icon": QIcon.fromTheme("application-exit"),
                "text": "&Exit",
                "status_tip": "Exit OCR Reader",
                "shortcut": "Ctrl+q",
                "trigger": self.parent.close,
            },
            "open_project_action": {
                "icon": QIcon.fromTheme("folder-open"),
                "text": "&Open Project",
                "status_tip": "Open Project",
                "shortcut": "Ctrl+o",
                "trigger": self.parent.project_actions.open_project,
            },
            "export_action": {
                "icon": QIcon.fromTheme("document-export"),
                "text": "&Export Project",
                "status_tip": "Export Project",
                "shortcut": "Ctrl+e",
                "trigger": self.parent.project_actions.export_project,
            },
            "save_project_action": {
                "icon": QIcon.fromTheme("document-save"),
                "text": "&Save Project",
                "status_tip": "Save Project",
                "shortcut": "Ctrl+s",
                "trigger": self.parent.project_actions.save_project,
            },
            "load_image_action": {
                "icon": QIcon.fromTheme("image-x-generic"),
                "text": "&Load Images or PDF",
                "status_tip": "Load Image",
                "shortcut": "Ctrl+i",
                "trigger": self.parent.file_actions.import_media_files,
            },
            "analyze_layout_action": {
                "icon": QIcon.fromTheme("system-search"),
                "text": "&Analyze Layout",
                "status_tip": "Analyze Layout",
                "shortcut": "Ctrl+Alt+a",
                "trigger": self.parent.ocr_actions.analyze_layout,
            },
            "recognize_ocr_action": {
                "icon": QIcon.fromTheme("text-x-bibtex"),
                "text": "&Recognize OCR",
                "status_tip": "Recognize OCR",
                "shortcut": "Ctrl+Alt+o",
                "trigger": self.parent.ocr_actions.recognize_boxes,
            },
            "analyze_layout_and_recognize_action": {
                "icon": QIcon.fromTheme("text-x-bibtex"),
                "text": "Analyze Layout and &Recognize",
                "status_tip": "Analyze Layout and Recognize",
                "shortcut": "Ctrl+Alt+r",
                "trigger": self.parent.ocr_actions.analyze_layout_and_recognize,
            },
            "open_train_model_dialog": {
                "icon": QIcon.fromTheme("system-run"),
                "text": "&Train Model",
                "status_tip": "Train Model",
                "shortcut": "Ctrl+Alt+t",
                "trigger": self.parent.model_training_actions.open_train_model_dialog,
            },
            "ocr_editor_action": {
                "icon": QIcon.fromTheme("document-edit"),
                "text": "OCR Editor",
                "status_tip": "OCR Editor",
                "shortcut": "Ctrl+Alt+e",
                "trigger": self.parent.page_actions.ocr_editor,
            },
            "ocr_editor_project_action": {
                "icon": QIcon.fromTheme("text-wrap-line"),
                "text": "OCR Editor Project",
                "status_tip": "OCR Editor Project",
                "shortcut": "Ctrl+Alt+p",
                "trigger": self.parent.page_actions.ocr_editor_project,
            },
            "close_project_action": {
                "icon": QIcon.fromTheme("close-symbol"),
                "text": "&Close project",
                "status_tip": "Close project",
                "shortcut": "Ctrl+w",
                "trigger": self.parent.project_actions.close_project,
            },
            "settings_action": {
                "icon": QIcon.fromTheme("preferences-system"),
                "text": "&Settings",
                "status_tip": "Settings",
                "shortcut": "Ctrl+p",
                "trigger": self.parent.show_settings_dialog,
            },
            "delete_selected_pages_action": {
                "icon": QIcon.fromTheme("edit-delete"),
                "text": "Delete",
                "status_tip": "Delete selected pages",
                "shortcut": "Delete",
            },
            "project_manager_action": {
                "icon": QIcon.fromTheme("system-file-manager"),
                "text": "&Project Manager",
                "status_tip": "Project Manager",
                "shortcut": "Ctrl+Shift+p",
                "trigger": self.parent.show_project_manager_dialog,
            },
            "import_pdf_action": {
                "icon": QIcon.fromTheme("application-pdf"),
                "text": "&Import PDF",
                "status_tip": "Import PDF",
                "shortcut": "Ctrl+Shift+i",
                "trigger": self.parent.file_actions.import_pdf,
            },
            "set_header_footer_for_project_action": {
                "icon": QIcon.fromTheme("preferences-desktop-display"),
                "text": "Set Header/Footer for Project from current page",
                "status_tip": "Set Header/Footer for Project",
                "shortcut": "Ctrl+Alt+h",
                "trigger": self.parent.page_actions.set_header_footer_for_project,
            },
            "analyze_project_action": {
                "icon": QIcon.fromTheme("system-search"),
                "text": "&Analyze Project",
                "status_tip": "Analyze Project",
                "shortcut": "Ctrl+Shift+a",
                "trigger": self.parent.project_actions.analyze_project,
            },
        }

        for action_name, info in actions_info.items():
            if "icon" in info:
                action = QAction(
                    info["icon"],
                    QCoreApplication.translate(action_name, info["text"]),
                    self.parent,
                )
            else:
                action = QAction(
                    QCoreApplication.translate(action_name, info["text"]),
                    self.parent,
                )
            action.setStatusTip(
                QCoreApplication.translate(action_name, info["status_tip"])
            )
            action.setShortcut(QKeySequence(info["shortcut"]))
            if "trigger" in info:
                action.triggered.connect(info["trigger"])
            setattr(self, action_name, action)

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
