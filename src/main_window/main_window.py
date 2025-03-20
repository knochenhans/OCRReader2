import os
from typing import List, Optional
from PySide6.QtCore import QCoreApplication, Slot
from PySide6.QtGui import QIcon, QCloseEvent, QUndoStack, Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QSplitter,
    QLabel,
    QTabWidget,
    QProgressBar,
    QMessageBox,
)

import darkdetect  # type: ignore
from iso639 import Lang
from platformdirs import user_data_dir  # type: ignore
from loguru import logger

from main_window.toolbar import Toolbar  # type: ignore
from main_window.menus import Menus  # type: ignore
from main_window.actions import Actions  # type: ignore
from main_window.user_actions import UserActions  # type: ignore
from main_window.page_icon_view import PagesIconView  # type: ignore
from settings import Settings  # type: ignore
from project.project_manager import ProjectManager  # type: ignore
from project.project_manager_dialog import ProjectManagerDialog  # type: ignore
from project.settings_dialog import SettingsDialog  # type: ignore
from page_editor.page_editor_view import PageEditorView  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from ocr_edit_dialog.ocr_editor_dialog import OCREditorDialog  # type: ignore
from main_window.box_properties_widget import BoxPropertiesWidget  # type: ignore
from page.ocr_box import OCRBox  # type: ignore
from exporter.exporter_widget import ExporterWidget  # type: ignore


class MainWindow(QMainWindow):
    APP_NAME = "OCRReader 2"
    LIGHT_THEME_FOLDER = "light-theme"
    DARK_THEME_FOLDER = "dark-theme"
    ICON_PATH = "resources/icons/{}/{}"

    def __init__(self) -> None:
        super().__init__()

        self.theme_folder = self.LIGHT_THEME_FOLDER

        self.undo_stack = QUndoStack(self)

        self.user_data_dir = user_data_dir("ocrreader", "ocrreader")

        self.application_settings = Settings("application_settings", self.user_data_dir)
        self.application_settings.load()

        self.setup_application()
        self.setup_ui()

        self.project_manager = ProjectManager(
            os.path.join(self.user_data_dir, "projects")
        )

        self.page_editor_controller: Optional[PageEditorController] = None

        self.user_actions = UserActions(
            self,
            self.page_editor_controller,
            self.project_manager,
            self.page_icon_view,
            self.page_editor_view,
        )

        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.settings_changed.connect(self.settings_changed)

        self.page_editor_view.user_actions = self.user_actions

        self.actions_ = Actions(self, self.theme_folder, self.ICON_PATH)
        self.toolbar = Toolbar(self)
        self.menus = Menus(self)

        self.toolbar.setup_toolbar(self.actions_)
        self.menus.setup_menus(self.actions_)

        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menus.menu_bar)

        self.custom_shortcuts: Optional[dict] = None
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
            lambda: self.user_actions.load_current_project()
        )
        self.project_manager_window.exec()

    def setup_application(self) -> None:
        QCoreApplication.setOrganizationName(self.APP_NAME)
        QCoreApplication.setOrganizationDomain(self.APP_NAME)
        QCoreApplication.setApplicationName(self.APP_NAME)

        if darkdetect.isLight():
            self.theme_folder = self.DARK_THEME_FOLDER

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
        self.user_actions.open_page(index)
        self.update_page_count_label(index + 1, total)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            filenames = []

            for url in event.mimeData().urls():
                filenames.append(url.toLocalFile())

            self.user_actions.add_images(filenames)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_application_settings()
        return super().closeEvent(event)

    def show_settings_dialog(self) -> None:
        # TODO: use fixed engine for now
        from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR  # type: ignore

        project = None

        if self.project_manager.current_project is not None:
            project = self.project_manager.current_project

        if project is not None:
            if project.settings is not None:
                self.settings_dialog.load_settings(
                    self.application_settings,
                    project.settings,
                    OCREngineTesserOCR().get_available_langs(),
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

    def on_page_icon_view_context_menu(self, point):
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

        if self.project_manager.current_project:
            if self.project_manager.current_project.settings:
                langs = self.project_manager.current_project.settings.get("langs")
                ocr_edit_dialog = OCREditorDialog(
                    self.project_manager.current_project.pages,
                    Lang(langs[0]).pt1,
                    self.application_settings,
                    for_project=True,
                )
        ocr_edit_dialog.exec()

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
