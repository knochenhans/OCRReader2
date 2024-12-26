from PySide6.QtCore import QCoreApplication, QSettings, QByteArray, QSize
from PySide6.QtGui import QIcon, QKeySequence, QCloseEvent, QAction, QUndoStack
from PySide6.QtWidgets import QMainWindow, QStatusBar, QToolBar, QMenu
import darkdetect  # type: ignore


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.app_name = "OCRReader 2"
        self.theme_folder = "light-theme"

        self.undo_stack = QUndoStack(self)

        self.setup_application()
        self.setup_ui()
        self.setup_toolbar()
        self.setup_menus()

        self.show()

        self.statusBar().showMessage(
            QCoreApplication.translate("status_loaded", "OCR Reader loaded")
        )
        self.showMaximized()

    def setup_application(self) -> None:
        QCoreApplication.setOrganizationName(self.app_name)
        QCoreApplication.setOrganizationDomain(self.app_name)
        QCoreApplication.setApplicationName(self.app_name)

        if darkdetect.isLight():
            self.theme_folder = "dark-theme"

    def setup_ui(self) -> None:
        self.setWindowTitle(self.app_name)
        self.setWindowIcon(
            QIcon(f"resources/icons/{self.theme_folder}/character-recognition-line.png")
        )
        self.setStatusBar(QStatusBar(self))
        self.setAcceptDrops(True)

    def setup_toolbar(self) -> None:
        self.toolbar = QToolBar("Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)

    def setup_menus(self) -> None:
        menu = self.menuBar()
        self.file_menu: QMenu = menu.addMenu(
            QCoreApplication.translate("menu_file", "&File")
        )
        self.edit_menu: QMenu = menu.addMenu(
            QCoreApplication.translate("menu_edit", "&Edit")
        )

        self.page_icon_view_context_menu = QMenu(self)

        self.setup_actions()
        self.setup_action_toolbar()
        self.setup_file_menu()
        self.setup_edit_menu()

    def setup_actions(self) -> None:
        self.exit_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/close-circle-line.png"),
            QCoreApplication.translate("action_exit", "&Exit"),
            self,
        )
        self.exit_action.setStatusTip(
            QCoreApplication.translate("status_exit", "Exit OCR Reader")
        )
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QKeySequence("Ctrl+q"))

        self.open_project_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/folder-4-line.png"),
            QCoreApplication.translate("action_open_project", "&Open Project"),
            self,
        )
        self.open_project_action.setStatusTip(
            QCoreApplication.translate("status_open_project", "Open Project")
        )
        self.open_project_action.setShortcut(QKeySequence("Ctrl+o"))

        self.export_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/folder-transfer-line.png"),
            QCoreApplication.translate("action_export_project", "&Export Project"),
            self,
        )
        self.export_action.setStatusTip(
            QCoreApplication.translate("status_export_project", "Export Project")
        )
        self.export_action.setShortcut(QKeySequence("Ctrl+e"))

        self.save_project_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/save-line.png"),
            QCoreApplication.translate("action_save_project", "&Save Project"),
            self,
        )
        self.save_project_action.setStatusTip(
            QCoreApplication.translate("status_save_project", "Save Project")
        )
        self.save_project_action.setShortcut(QKeySequence("Ctrl+s"))

        self.load_image_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/image-line.png"),
            QCoreApplication.translate("action_load_image", "&Load Image or PDF"),
            self,
        )
        self.load_image_action.setStatusTip(
            QCoreApplication.translate("status_load_image", "Load Image")
        )
        self.load_image_action.setShortcut(QKeySequence("Ctrl+i"))

        self.analyze_layout_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/layout-line.png"),
            QCoreApplication.translate("action_analyze_layout", "&Analyze Layout"),
            self,
        )
        self.analyze_layout_action.setStatusTip(
            QCoreApplication.translate("status_analyze_layout", "Analyze Layout")
        )
        self.analyze_layout_action.setShortcut(QKeySequence("Ctrl+Alt+a"))

        self.analyze_layout_and_recognize_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/layout-fill.png"),
            QCoreApplication.translate(
                "action_analyze_layout_and_recognize", "Analyze Layout and &Recognize"
            ),
            self,
        )
        self.analyze_layout_and_recognize_action.setStatusTip(
            QCoreApplication.translate(
                "status_analyze_layout_and_recognize", "Analyze Layout and Recognize"
            )
        )
        self.analyze_layout_and_recognize_action.setShortcut(QKeySequence("Ctrl+Alt+r"))

        self.close_project_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/close-line.png"),
            QCoreApplication.translate("action_close_project", "&Close project"),
            self,
        )
        self.close_project_action.setStatusTip(
            QCoreApplication.translate("status_close_project", "Close project")
        )
        self.close_project_action.setShortcut(QKeySequence("Ctrl+w"))

        self.undo_action = self.undo_stack.createUndoAction(
            self, QCoreApplication.translate("Undo", "&Undo")
        )
        self.undo_action.setIcon(
            QIcon(f"resources/icons/{self.theme_folder}/arrow-go-back-line.png")
        )
        self.undo_action.setShortcut(QKeySequence("Ctrl+z"))

        self.redo_action = self.undo_stack.createRedoAction(
            self, QCoreApplication.translate("Redo", "&Redo")
        )
        self.redo_action.setIcon(
            QIcon(f"resources/icons/{self.theme_folder}/arrow-go-forward-line.png")
        )
        self.redo_action.setShortcut(QKeySequence("Ctrl+y"))

        self.preferences_action = QAction(
            QIcon(f"resources/icons/{self.theme_folder}/settings-3-line.png"),
            QCoreApplication.translate("action_preferences", "&Preferences"),
            self,
        )
        self.preferences_action.setStatusTip(
            QCoreApplication.translate("status_preferences", "Preferences")
        )
        self.preferences_action.setShortcut(QKeySequence("Ctrl+p"))

        self.delete_selected_pages_action = QAction(
            QCoreApplication.translate("delete_pages", "Delete"), self
        )
        self.delete_selected_pages_action.setShortcut(QKeySequence("Delete"))

        self.page_icon_view_context_menu.addAction(self.load_image_action)

    def setup_action_toolbar(self):
        self.toolbar.addAction(self.load_image_action)
        self.toolbar.addAction(self.open_project_action)
        self.toolbar.addAction(self.save_project_action)
        self.toolbar.addAction(self.export_action)
        self.toolbar.addAction(self.analyze_layout_action)
        self.toolbar.addAction(self.analyze_layout_and_recognize_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)

    def setup_file_menu(self):
        self.file_menu.addAction(self.load_image_action)
        self.file_menu.addAction(self.open_project_action)
        self.file_menu.addAction(self.save_project_action)
        self.file_menu.addAction(self.close_project_action)
        self.file_menu.addAction(self.export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

    def setup_edit_menu(self):
        self.edit_menu.addAction(self.preferences_action)
        self.file_menu.addSeparator()
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

    def load_images(self, filenames):
        pass

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            filenames = []

            for url in event.mimeData().urls():
                filenames.append(url.toLocalFile())

            self.load_images(filenames)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_settings()
        return super().closeEvent(event)

    def save_settings(self) -> None:
        #     self.settings.setValue("geometry", self.saveGeometry())
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
