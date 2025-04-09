from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QIcon, QKeySequence


class Actions:
    def __init__(self, parent, theme_folder: str, icon_path: str) -> None:
        self.parent = parent
        self.theme_folder: str = theme_folder
        self.icon_path: str = icon_path
        self.create_actions()

    def create_actions(self) -> None:
        actions_info = {
            "exit_action": {
                "icon": "close-circle-line.png",
                "text": "&Exit",
                "status_tip": "Exit OCR Reader",
                "shortcut": "Ctrl+q",
                "trigger": self.parent.close,
            },
            "open_project_action": {
                "icon": "folder-4-line.png",
                "text": "&Open Project",
                "status_tip": "Open Project",
                "shortcut": "Ctrl+o",
                "trigger": self.parent.project_actions.open_project,
            },
            "export_action": {
                "icon": "folder-transfer-line.png",
                "text": "&Export Project",
                "status_tip": "Export Project",
                "shortcut": "Ctrl+e",
                "trigger": self.parent.project_actions.export_project,
            },
            "save_project_action": {
                "icon": "save-line.png",
                "text": "&Save Project",
                "status_tip": "Save Project",
                "shortcut": "Ctrl+s",
                "trigger": self.parent.project_actions.save_project,
            },
            "load_image_action": {
                "icon": "image-line.png",
                "text": "&Load Images or PDF",
                "status_tip": "Load Image",
                "shortcut": "Ctrl+i",
                "trigger": self.parent.file_actions.import_media_files,
            },
            "analyze_layout_action": {
                "icon": "layout-line.png",
                "text": "&Analyze Layout",
                "status_tip": "Analyze Layout",
                "shortcut": "Ctrl+Alt+a",
                "trigger": self.parent.ocr_actions.analyze_layout,
            },
            "recognize_ocr_action": {
                "icon": "ocr-line.png",
                "text": "&Recognize OCR",
                "status_tip": "Recognize OCR",
                "shortcut": "Ctrl+Alt+o",
                "trigger": self.parent.ocr_actions.recognize_boxes,
            },
            "analyze_layout_and_recognize_action": {
                "icon": "layout-fill.png",
                "text": "Analyze Layout and &Recognize",
                "status_tip": "Analyze Layout and Recognize",
                "shortcut": "Ctrl+Alt+r",
                "trigger": self.parent.ocr_actions.analyze_layout_and_recognize,
            },
            "open_train_model_dialog": {
                "icon": "train-line.png",
                "text": "&Train Model",
                "status_tip": "Train Model",
                "shortcut": "Ctrl+Alt+t",
                "trigger": self.parent.model_training_actions.open_train_model_dialog,
            },
            "ocr_editor_action": {
                "icon": "text-wrap-line.png",
                "text": "OCR Editor",
                "status_tip": "OCR Editor",
                "shortcut": "Ctrl+Alt+e",
                "trigger": self.parent.page_actions.ocr_editor,
            },
            "ocr_editor_project_action": {
                "icon": "text-wrap-line.png",
                "text": "OCR Editor Project",
                "status_tip": "OCR Editor Project",
                "shortcut": "Ctrl+Alt+p",
                "trigger": self.parent.page_actions.ocr_editor_project,
            },
            "close_project_action": {
                "icon": "close-line.png",
                "text": "&Close project",
                "status_tip": "Close project",
                "shortcut": "Ctrl+w",
                "trigger": self.parent.project_actions.close_project,
            },
            "settings_action": {
                "icon": "settings-3-line.png",
                "text": "&Settings",
                "status_tip": "Settings",
                "shortcut": "Ctrl+p",
                "trigger": self.parent.show_settings_dialog,
            },
            "delete_selected_pages_action": {
                "text": "Delete",
                "status_tip": "Delete selected pages",
                "shortcut": "Delete",
            },
            "project_manager_action": {
                "icon": "folder-line.png",
                "text": "&Project Manager",
                "status_tip": "Project Manager",
                "shortcut": "Ctrl+Shift+p",
                "trigger": self.parent.show_project_manager_dialog,
            },
            "import_pdf_action": {
                "icon": "file-pdf-line.png",
                "text": "&Import PDF",
                "status_tip": "Import PDF",
                "shortcut": "Ctrl+Shift+i",
                "trigger": self.parent.file_actions.import_pdf,
            },
            "set_header_footer_for_project_action": {
                "text": "Set Header/Footer for Project from current page",
                "status_tip": "Set Header/Footer for Project",
                "shortcut": "Ctrl+Alt+h",
                "trigger": self.parent.page_actions.set_header_footer_for_project,
            },
            "analyze_project_action": {
                "icon": "layout-2-line.png",
                "text": "&Analyze Project",
                "status_tip": "Analyze Project",
                "shortcut": "Ctrl+Shift+a",
                "trigger": self.parent.project_actions.analyze_project,
            },
        }

        for action_name, info in actions_info.items():
            if "icon" in info:
                action = QAction(
                    QIcon(self.icon_path.format(self.theme_folder, info["icon"])),
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
