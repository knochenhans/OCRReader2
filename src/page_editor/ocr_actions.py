class OCRActions:
    def __init__(self, main_window) -> None:
        self.main_window = main_window

    def analyze_layout(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        controller = self.main_window.page_editor_view.page_editor_scene.controller
        if not controller:
            return

        current_page = controller.page
        if controller.has_box_items():
            response = self.main_window.show_confirmation_dialog(
                "Existing boxes detected",
                "There are existing box items. Do you want to delete them before analyzing the layout?",
            )
            if response:
                controller.clear_box_items()

        self.main_window.show_status_message("Analyzing layout")
        current_page.analyze_page()

    def recognize_boxes(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        self.main_window.show_status_message("Recognizing OCR boxes")
        controller = self.main_window.page_editor_view.page_editor_scene.controller
        if not controller:
            return

        current_page = controller.page
        current_page.recognize_ocr_boxes(
            progress_callback=self.main_window.update_progress_bar
        )
        self.main_window.ocr_editor()

    def analyze_layout_and_recognize(self) -> None:
        if not self.main_window.page_editor_view.page_editor_scene:
            return

        self.main_window.show_status_message("Analyzing layout and recognizing")
        controller = self.main_window.page_editor_view.page_editor_scene.controller

        if not controller:
            return

        current_page = controller.page
        current_page.analyze_page()
        current_page.recognize_ocr_boxes(
            progress_callback=self.main_window.update_progress_bar
        )
