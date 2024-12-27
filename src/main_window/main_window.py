from PySide6.QtCore import QCoreApplication, QSettings, QByteArray, QSize
from PySide6.QtGui import QIcon, QKeySequence, QCloseEvent, QAction, QUndoStack
from PySide6.QtWidgets import QMainWindow, QStatusBar, QToolBar, QMenu
import darkdetect  # type: ignore

from main_window.toolbar import Toolbar  # type: ignore
from main_window.menus import Menus  # type: ignore
from main_window.actions import Actions  # type: ignore
from main_window.user_actions import UserActions  # type: ignore


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

        self.user_actions = UserActions(self)
        self.actions_ = Actions(self, self.theme_folder, self.ICON_PATH)
        self.toolbar = Toolbar(self)
        self.menus = Menus(self)

        self.toolbar.setup_toolbar(self.actions_)
        self.menus.setup_menus(self.actions_)

        self.addToolBar(self.toolbar)
        self.setMenuBar(self.menus.menu_bar)

        self.show()

        self.statusBar().showMessage(
            QCoreApplication.translate("status_loaded", "OCR Reader loaded")
        )
        self.showMaximized()

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
        self.setStatusBar(QStatusBar(self))
        self.setAcceptDrops(True)

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

    # def on_page_icon_view_context_menu(self, point):
    #     if self.page_icon_view.selectedIndexes():
    #         self.page_icon_view_context_menu.addAction(
    #             self.delete_selected_pages_action
    #         )
    #         self.page_icon_view_context_menu.addAction(self.analyze_layout_action)
    #         self.page_icon_view_context_menu.addAction(
    #             self.analyze_layout_and_recognize_action
    #         )

    #     action = self.page_icon_view_context_menu.exec_(
    #         self.page_icon_view.mapToGlobal(point)
    #     )

    #     if action == self.delete_selected_pages_action:
    #         self.page_icon_view.remove_selected_pages()
    #         self.update()
