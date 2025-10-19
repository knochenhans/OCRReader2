import os
from typing import Dict, List, Optional

from iso639 import Lang
from platformdirs import user_data_dir
from PySide6.QtCore import QCoreApplication, QPoint, Slot
from PySide6.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QKeySequence,
    Qt,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QTabWidget,
)
from SettingsManager import SettingsManager

from OCRReader2.box_properties import BoxPropertiesWidget
from OCRReader2.exporter.exporter_widget import ExporterWidget
from OCRReader2.main_window.actions import Actions
from OCRReader2.main_window.file_actions import FileActions
from OCRReader2.main_window.menus import Menus
from OCRReader2.main_window.model_training_actions import ModelTrainingActions
from OCRReader2.main_window.page_actions import PageActions
from OCRReader2.main_window.page_icon_view import PagesIconView
from OCRReader2.main_window.project_actions import ProjectActions
from OCRReader2.main_window.toolbar import Toolbar
from OCRReader2.ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog
from OCRReader2.ocr_edit_dialog.ocr_editor_dialog_merged import OCREditorDialogMerged
from OCRReader2.page.ocr_box import OCRBox
from OCRReader2.page_editor.ocr_actions import OCRActions
from OCRReader2.page_editor.page_editor_controller import PageEditorController
from OCRReader2.page_editor.page_editor_view import PageEditorView
from OCRReader2.project.project_manager import ProjectManager
from OCRReader2.project.project_manager_dialog import ProjectManagerDialog
from OCRReader2.settings.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    APP_NAME = "OCRReader 2"
    LIGHT_THEME_FOLDER = "light-theme"
    DARK_THEME_FOLDER = "dark-theme"
    ICON_PATH = "resources/icons/{}/{}"

    def __init__(self) -> None:
        super().__init__()

        self.theme_folder = self.LIGHT_THEME_FOLDER
        self.box_ids_flagged_for_training: List[str] = []

        self.undo_stack = QUndoStack(self)

        self.user_data_dir = user_data_dir("ocrreader", "ocrreader")

        SettingsManager.set_app_name(self.APP_NAME)
        self.application_settings = SettingsManager("application_settings")
        self.application_settings.load()

        self.setup_application()
        self.setup_ui()

        self.project_manager = ProjectManager(
            os.path.join(self.user_data_dir, "projects")
        )

        self.page_editor_controller: Optional[PageEditorController] = None

        self.page_actions = PageActions(
            self, self.project_manager, self.page_icon_view, self.page_editor_view
        )

        self.ocr_actions = OCRActions(self)
        self.project_actions = ProjectActions(
            self,
            self.project_manager,
            self.page_icon_view,
            self.page_editor_view,
            self.page_actions,
        )
        self.file_actions = FileActions(self, self.project_manager)
        self.model_training_actions = ModelTrainingActions(self, self.project_manager)

        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.settings_changed.connect(self.settings_changed)

        self.page_editor_view.page_actions = self.page_actions
        self.page_editor_view.ocr_actions = self.ocr_actions

        self.actions_ = Actions(self, self.theme_folder, self.ICON_PATH)
        self.toolbar = Toolbar(self)
        self.menus = Menus(self)

        self.toolbar.setup_toolbar(self.actions_)
        self.menus.setup_menus(self.actions_)

        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menus.menu_bar)

        self.custom_shortcuts: Optional[Dict[str, QKeySequence]] = None
        self.restore_application_settings()

        self.show_status_message(
            QCoreApplication.translate("status_loaded", "OCR Reader loaded")
        )
        self.showMaximized()

        self.show_project_manager_dialog()

    def show_project_manager_dialog(self):
        self.project_manager_window = ProjectManagerDialog(
            self.project_manager, self, self.update_progress_bar
        )
        self.project_manager_window.project_opened.connect(
            lambda: self.project_actions.load_current_project()
        )
        self.project_manager_window.exec()

    def setup_application(self) -> None:
        QCoreApplication.setOrganizationName(self.APP_NAME)
        QCoreApplication.setOrganizationDomain(self.APP_NAME)
        QCoreApplication.setApplicationName(self.APP_NAME)

        # if darkdetect.isLight():
        #     self.theme_folder = self.DARK_THEME_FOLDER

    def setup_ui(self) -> None:
        self.setWindowTitle(self.APP_NAME)
        self.setWindowIcon(
            QIcon(
                self.ICON_PATH.format(
                    self.theme_folder, "character-recognition-line.png"
                )
            )
        )
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.setAcceptDrops(True)

        self.project_name_label = QLabel("No project loaded")
        self.status_bar.addPermanentWidget(self.project_name_label)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.edit_status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.edit_status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.page_count_label = QLabel("Pages: 0 of 0")
        self.status_bar.addPermanentWidget(self.page_count_label)

        self.page_icon_view = PagesIconView(self.application_settings, self)
        self.page_icon_view.customContextMenuRequested.connect(
            self.on_page_icon_view_context_menu
        )
        self.page_icon_view.current_page_changed.connect(self.current_page_changed)

        self.box_properties_widget = BoxPropertiesWidget()
        self.exporter_widget = ExporterWidget(self.application_settings, self)
        self.page_editor_view = PageEditorView(
            self.application_settings, progress_callback=self.update_progress_bar
        )

        self.page_editor_view.setMinimumWidth(500)
        self.page_editor_view.box_selection_changed.connect(
            self.on_box_selection_changed
        )
        self.page_editor_view.edit_state_changed.connect(self.update_edit_status)
        self.page_editor_view.box_double_clicked.connect(self.ocr_editor)

        self.splitter_2 = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_2.addWidget(self.page_editor_view)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.box_properties_widget, "Box Properties")
        self.tab_widget.addTab(self.exporter_widget, "Exporter")

        self.splitter_2.addWidget(self.tab_widget)
        self.splitter_2.setSizes([2000, 1])

        self.splitter_1 = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_1.addWidget(self.page_icon_view)
        self.splitter_1.addWidget(self.splitter_2)
        self.splitter_1.setSizes([1, 10])

        self.setCentralWidget(self.splitter_1)

    def settings_changed(self):
        pass

    @Slot()
    def on_box_selection_changed(self, ocr_boxes: List[OCRBox]):
        self.box_properties_widget.set_box(ocr_boxes)

    def current_page_changed(self, index: int, total: int):
        self.page_actions.open_page(index)
        self.update_page_count_label(index + 1, total)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            filenames: List[str] = []

            for url in event.mimeData().urls():
                filenames.append(url.toLocalFile())

            self.file_actions.add_images(filenames)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_application_settings()
        return super().closeEvent(event)

    def show_settings_dialog(self) -> None:
        # TODO: use fixed engine for now
        from OCRReader2.ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR

        project = None

        if self.project_manager.current_project is not None:
            project = self.project_manager.current_project

        if project is not None:
            if project.settings_manager is not None:
                self.settings_dialog.load_settings(
                    self.application_settings,
                    project.settings_manager,
                    OCREngineTesserOCR(project.settings_manager).get_available_langs(),
                    (
                        self.custom_shortcuts
                        if isinstance(self.custom_shortcuts, dict)
                        else {}
                    ),
                )
                self.settings_dialog.show()

    def restore_application_settings(self) -> None:
        width = self.application_settings.settings.get("width", 1280)
        height = self.application_settings.settings.get("height", 800)
        pos_x = self.application_settings.settings.get("pos_x", 100)
        pos_y = self.application_settings.settings.get("pos_y", 100)
        is_maximized = self.application_settings.settings.get("is_maximized", False)

        self.resize(width, height)
        self.move(pos_x, pos_y)
        if is_maximized:
            self.showMaximized()

        self.custom_shortcuts = self.application_settings.settings.get(
            "custom_shortcuts", {}
        )
        if self.custom_shortcuts:
            self.page_editor_view.custom_shortcuts = self.custom_shortcuts

    def save_application_settings(self) -> None:
        if self.isMaximized():
            self.application_settings.settings["is_maximized"] = True
        else:
            self.application_settings.settings["is_maximized"] = False
            self.application_settings.settings["width"] = self.width()
            self.application_settings.settings["height"] = self.height()
            self.application_settings.settings["pos_x"] = self.x()
            self.application_settings.settings["pos_y"] = self.y()

        self.application_settings.settings["custom_shortcuts"] = self.custom_shortcuts
        self.application_settings.save()

    def on_page_icon_view_context_menu(self, point: QPoint) -> None:
        # if self.page_icon_view.selectedIndexes():
        #     self.page_icon_view_context_menu.addAction(
        #         self.delete_selected_pages_action
        #     )
        #     self.page_icon_view_context_menu.addAction(self.analyze_layout_action)
        #     self.page_icon_view_context_menu.addAction(
        #         self.analyze_layout_and_recognize_action
        #     )

        # action = self.page_icon_view_context_menu.exec_(
        #     self.page_icon_view.mapToGlobal(point)
        # )

        # if action == self.delete_selected_pages_action:
        #     self.page_icon_view.remove_selected_pages()
        #     self.update()
        pass

    def show_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def focusNextChild(self) -> bool:
        return False

    def ocr_editor_project(self) -> None:
        if not self.project_manager:
            return

        ocr_edit_dialog: Optional[OCREditorDialog] = None

        if self.project_manager.current_project:
            if self.project_manager.current_project.settings_manager:
                langs = self.project_manager.current_project.settings_manager.get(
                    "langs"
                )
                ocr_edit_dialog = OCREditorDialog(
                    self.project_manager.current_project.pages,
                    Lang(langs[0]).pt1,
                    self.application_settings,
                    for_project=True,
                    box_ids_flagged_for_training=self.box_ids_flagged_for_training,
                )
                ocr_edit_dialog.box_flagged_for_training.connect(
                    self.on_box_flagged_for_training
                )

        if ocr_edit_dialog:
            ocr_edit_dialog.exec()

    def ocr_editor_merged(self) -> None:
        if not self.project_manager:
            return

        ocr_edit_dialog: Optional[OCREditorDialogMerged] = None

        if self.project_manager.current_project:
            if self.project_manager.current_project.settings_manager:
                langs = self.project_manager.current_project.settings_manager.get(
                    "langs"
                )
                ocr_edit_dialog = OCREditorDialogMerged(
                    self.project_manager.current_project.pages,
                    Lang(langs[0]).pt1,
                    self.application_settings,
                    box_ids_flagged_for_training=self.box_ids_flagged_for_training,
                )
                ocr_edit_dialog.box_flagged_for_training.connect(
                    self.on_box_flagged_for_training
                )

        if ocr_edit_dialog:
            ocr_edit_dialog.exec()

    @Slot()
    def on_box_flagged_for_training(self, box_id: str, flag: bool) -> None:
        if flag:
            if box_id not in self.box_ids_flagged_for_training:
                self.box_ids_flagged_for_training.append(box_id)
        else:
            if box_id in self.box_ids_flagged_for_training:
                self.box_ids_flagged_for_training.remove(box_id)

        if self.project_manager.current_project:
            if self.project_manager.current_project.settings_manager:
                self.project_manager.current_project.settings_manager.set(
                    "flagged_box_ids", self.box_ids_flagged_for_training
                )

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.No)

        result = dialog.exec()
        return result == QMessageBox.StandardButton.Yes

    def update_progress_bar(self, value: int, total: int, message: str = "") -> None:
        self.progress_bar.setVisible(True)
        self.progress_bar.show()
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(value)

        if message:
            self.show_status_message(message)

        if value == total:
            self.progress_bar.setVisible(False)

        self.progress_bar.hide()
        self.progress_bar.update()
        self.progress_bar.repaint()

    @Slot()
    def update_edit_status(self, message: str) -> None:
        self.edit_status_label.setText(f"Page Editor State: {message}")
        self.edit_status_label.repaint()
        self.edit_status_label.update()

    def update_page_count_label(self, count: int, total: int) -> None:
        self.page_count_label.setText(f"Pages: {count} of {total}")
        self.page_count_label.repaint()
        self.page_count_label.update()

    def ocr_editor(self, box_id: str = "") -> None:
        if not self.project_manager:
            return

        if not self.project_manager.current_project:
            return

        project_settings = self.project_manager.current_project.settings_manager

        if not project_settings:
            return

        if not self.page_editor_view.page_editor_scene:
            return

        if not self.page_editor_view.page_editor_scene.controller:
            return

        langs = project_settings.get("langs")
        if langs and self.application_settings:
            ocr_edit_dialog = OCREditorDialog(
                [self.page_editor_view.page_editor_scene.controller.page],
                Lang(langs[0]).pt1,
                self.application_settings,
                box_id,
                box_ids_flagged_for_training=self.box_ids_flagged_for_training,
            )
            ocr_edit_dialog.box_flagged_for_training.connect(
                self.on_box_flagged_for_training
            )
            ocr_edit_dialog.exec()
