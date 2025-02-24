from typing import Optional
from PySide6.QtCore import QCoreApplication, QSettings, QByteArray, QSize, Slot
from PySide6.QtGui import QIcon, QKeySequence, QCloseEvent, QAction, QUndoStack, Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QToolBar,
    QMenu,
    QSplitter,
    QTextEdit,
    QLabel,
)

import darkdetect  # type: ignore
from platformdirs import user_data_dir  # type: ignore

from main_window.toolbar import Toolbar  # type: ignore
from main_window.menus import Menus  # type: ignore
from main_window.actions import Actions  # type: ignore
from main_window.user_actions import UserActions  # type: ignore
from main_window.page_icon_view import PagesIconView  # type: ignore
from project.project_settings import ProjectSettings  # type: ignore
from project.project_manager import ProjectManager  # type: ignore
from project.project_manager_window import ProjectManagerWindow  # type: ignore
from page_editor.page_editor_view import PageEditorView # type: ignore
from page_editor.page_editor_controller import PageEditorController  # type: ignore

project_settings = ProjectSettings(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "/tmp/ocrreader/export",
        "export_preview_path": "/tmp/ocrreader/preview",
    }
)


class MainWindow(QMainWindow):
    APP_NAME = "OCRReader 2"
    LIGHT_THEME_FOLDER = "light-theme"
    DARK_THEME_FOLDER = "dark-theme"
    ICON_PATH = "resources/icons/{}/{}"

    def __init__(self) -> None:
        super().__init__()

        self.theme_folder = self.LIGHT_THEME_FOLDER

        self.undo_stack = QUndoStack(self)

        self.setup_application()
        self.load_settings()
        self.setup_ui()

        data_dir = user_data_dir("ocrreader", "ocrreader")

        self.project_manager = ProjectManager(data_dir)

        self.project_settings = project_settings

        self.page_editor_controller: Optional[PageEditorController] = None
        self.current_project = None

        self.project_manager_window = ProjectManagerWindow(self.project_manager)
        self.project_manager_window.project_opened.connect(self.load_current_project)

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

    def save_settings(self) -> None:
        self.settings.setValue("geometry", self.saveGeometry())
        pass

    def load_settings(self) -> None:
        self.settings = QSettings()

        value = self.settings.value("geometry")

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

    def show_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message)
