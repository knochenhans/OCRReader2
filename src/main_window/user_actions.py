from PySide6.QtCore import QObject


class UserActions(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def load_images(self, filenames):
        # Implement the logic to load images
        print(f"Loading images: {filenames}")

    def open_project(self):
        # Implement the logic to open a project
        print("Opening project")

    def save_project(self):
        # Implement the logic to save a project
        print("Saving project")

    def export_project(self):
        # Implement the logic to export a project
        print("Exporting project")

    def analyze_layout(self):
        # Implement the logic to analyze layout
        print("Analyzing layout")

    def analyze_layout_and_recognize(self):
        # Implement the logic to analyze layout and recognize
        print("Analyzing layout and recognizing")
