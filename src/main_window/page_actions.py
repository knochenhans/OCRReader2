class PageActions:
    def __init__(
        self, main_window, project_manager, page_icon_view, page_editor_view
    ) -> None:
        self.main_window = main_window
        self.project_manager = project_manager
        self.page_icon_view = page_icon_view
        self.page_editor_view = page_editor_view

    def open_page(self, page_index: int) -> None:
        project = self.project_manager.current_project
        if project is None:
            return

        self.page_icon_view.open_page(page_index)
        self.project_manager.get_ocr_results_for_page(project, page_index)
        self.page_editor_view.project_settings = project.settings
        self.page_editor_view.set_page(project.pages[page_index])

    def next_page(self) -> None:
        if self.project_manager.current_project is None:
            return

        current_page_index: int = self.page_icon_view.get_current_page_index()
        next_page_index: int = current_page_index + 1

        if next_page_index < len(self.project_manager.current_project.pages):
            self.open_page(next_page_index)

    def previous_page(self) -> None:
        if self.project_manager.current_project is None:
            return

        current_page_index: int = self.page_icon_view.get_current_page_index()
        previous_page_index: int = current_page_index - 1

        if previous_page_index >= 0:
            self.open_page(previous_page_index)

    def ocr_editor(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        controller.ocr_editor()

    def ocr_editor_project(self) -> None:
        self.main_window.ocr_editor_project()

    def set_header_footer_for_project(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        project = self.project_manager.current_project

        if not project:
            return

        for page in project.pages:
            page.set_header(controller.page.layout.header_y)
            page.set_footer(controller.page.layout.footer_y)

    def set_box_flow(self) -> None:
        view = self.main_window.page_editor_view

        if not view:
            return

        view.start_box_flow_selection()
