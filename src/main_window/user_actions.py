class UserActions:
    def __init__(
        self, main_window, page_editor_controller, project_manager, page_icon_view, page_editor_view
    ):
        from main_window.main_window import MainWindow  # type: ignore
        from page_editor.page_editor_controller import PageEditorController  # type: ignore
        from project.project_manager import ProjectManager  # type: ignore
        from main_window.page_icon_view import PagesIconView
        from page_editor.page_editor_view import PageEditorView

        self.main_window: MainWindow = main_window
        self.page_editor_controller: PageEditorController = page_editor_controller
        self.project_manager: ProjectManager = project_manager
        self.page_icon_view: PagesIconView = page_icon_view
        self.page_editor_view: PageEditorView = page_editor_view

    def load_images(self, filenames):
        print(f"Loading images: {filenames}")

        if self.page_editor_controller:
            self.page_editor_controller.load_page()

    def open_project(self):
        print("Opening project")

        project = self.project_manager.get_project(-1)
        project.set_settings(self.main_window.project_settings)

        for index, page in enumerate(project.pages):
            page_data = {
                "number": index + 1,
            }
            self.page_icon_view.add_page(page.image_path, page_data)

        self.page_icon_view.select_first_page()
        self.page_editor_view.set_page(project.pages[0])

    def save_project(self):
        print("Saving project")

    def export_project(self):
        print("Exporting project")

    def analyze_layout(self):
        print("Analyzing layout")

    def analyze_layout_and_recognize(self):
        print("Analyzing layout and recognizing")
