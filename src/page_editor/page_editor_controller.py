from page.page import Page # type: ignore


class PageEditorController:
    def __init__(self, page: Page, scene):
        self.page = page
        self.scene = scene

    # def update_box_position(self, box_id, new_position):
    #     # Update the OCRBox in the Page
    #     box = self.page.get_box_by_id(box_id)
    #     if box:
    #         box.position = new_position
    #         # Notify the scene to update the visual representation
    #         self.scene.update_box_visual(box_id, new_position)
