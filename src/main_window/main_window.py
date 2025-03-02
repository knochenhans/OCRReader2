import os
import shutil
from typing import Optional
from PySide6.QtCore import QCoreApplication, QSettings, QByteArray, Slot
from PySide6.QtGui import QIcon, QCloseEvent, QUndoStack, Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QSplitter,
    QLabel,
)

import darkdetect  # type: ignore
from iso639 import Lang
from platformdirs import user_data_dir  # type: ignore

from main_window.toolbar import Toolbar  # type: ignore
from main_window.menus import Menus  # type: ignore
from main_window.actions import Actions  # type: ignore
from main_window.user_actions import UserActions  # type: ignore
from main_window.page_icon_view import PagesIconView  # type: ignore
from project.project_settings import ProjectSettings  # type: ignore
from project.project_manager import ProjectManager  # type: ignore
from project.project_manager_window import ProjectManagerWindow  # type: ignore
from project.settings_dialog import SettingsDialog  # type: ignore
from page_editor.page_editor_view import PageEditorView  # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore
from project.project import Project  # type: ignore
from ocr_edit_dialog.ocr_edit_dialog import OCREditDialog  # type: ignore


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

        self.setup_application()
        self.setup_application_settings()
        self.setup_ui()

        self.project_manager = ProjectManager(
            os.path.join(self.user_data_dir, "projects")
        )

        self.page_editor_controller: Optional[PageEditorController] = None
        self.current_project: Optional[Project] = None

        self.project_manager_window = ProjectManagerWindow(self.project_manager)
        self.project_manager_window.project_opened.connect(self.load_current_project)

        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.settings_changed.connect(self.settings_changed)

        self.user_actions = UserActions(
            self,
            self.page_editor_controller,
            self.project_manager,
            self.page_icon_view,
            self.page_editor_view,
        )
        self.actions_ = Actions(self, self.theme_folder, self.ICON_PATH)
        self.toolbar = Toolbar(self)
        self.menus = Menus(self)

        self.toolbar.setup_toolbar(self.actions_)
        self.menus.setup_menus(self.actions_)

        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menus.menu_bar)

        self.show()

        self.show_status_message(
            QCoreApplication.translate("status_loaded", "OCR Reader loaded")
        )
        self.showMaximized()

        self.project_manager_window.exec()

    # def setup_project_settings(self, data_dir: str) -> None:
    #     default_settings_path = os.path.join(
    #         os.path.dirname(__file__), "default_settings.json"
    #     )

    #     user_settings_path = os.path.join(data_dir, self.USER_SETTINGS_FILENAME)
    #     if not os.path.exists(user_settings_path):
    #         shutil.copyfile(
    #             default_settings_path,
    #             os.path.join(data_dir, self.USER_SETTINGS_FILENAME),
    #         )

    #     self.project_settings = ProjectSettings()
    #     self.project_settings.load(os.path.join(data_dir, self.USER_SETTINGS_FILENAME))

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

        self.edit_status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.edit_status_label)

        self.page_icon_view = PagesIconView(self)
        self.page_icon_view.customContextMenuRequested.connect(
            self.on_page_icon_view_context_menu
        )

        # self.splitter_2 = QSplitter(Qt.Orientation.Vertical)
        # self.splitter_2.setSizes([1, 1])

        self.page_editor_view = PageEditorView()
        self.page_editor_view.setMinimumWidth(500)

        self.splitter_1 = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_1.addWidget(self.page_icon_view)
        self.splitter_1.addWidget(self.page_editor_view)
        self.splitter_1.setSizes([1, 1])

        self.setCentralWidget(self.splitter_1)

    def settings_changed(self):
        pass

    def current_page_changed(self, index):
        self.user_actions.open_page(index)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            filenames = []

            for url in event.mimeData().urls():
                filenames.append(url.toLocalFile())

            self.user_actions.load_images(filenames)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_settings()
        return super().closeEvent(event)

    def show_settings_dialog(self) -> None:
        # TODO: use fixed engine for now
        from ocr_engine.ocr_engine_tesserocr import OCREngineTesserOCR  # type: ignore

        if self.current_project is not None:
            self.settings_dialog.load_settings(
                self.current_project.settings,
                OCREngineTesserOCR().get_available_langs(),
            )
            self.settings_dialog.show()

    def save_settings(self) -> None:
        self.application_settings.setValue("geometry", self.saveGeometry())

    def setup_application_settings(self) -> None:
        self.application_settings = QSettings()

        value = self.application_settings.value("geometry")

        if isinstance(value, QByteArray):
            geometry: QByteArray = value

            if geometry:
                self.restoreGeometry(geometry)
            else:
                self.resize(1280, 800)

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

    @Slot()
    def load_current_project(self):
        project = self.project_manager.current_project

        if project is not None:
            self.user_actions.load_project(project.uuid)
            self.project_name_label.setText(f"Current project: {project.name}")
            self.page_icon_view.current_page_changed.connect(self.current_page_changed)
            self.current_project = project

    def show_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def focusNextChild(self) -> bool:
        return False

    def ocr_editor_project(self) -> None:
        if self.project_manager.current_project:
            langs = self.project_manager.current_project.settings.get("langs")
            ocr_edit_dialog = OCREditDialog(
                self.project_manager.current_project.pages, Lang(langs[0]).pt1
            )
        ocr_edit_dialog.exec()
