import os
from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from model_trainer.custom_text_editor import CustomTextEditor


class ModelTrainerDialog(QDialog):
    train_button_clicked = Signal()

    def __init__(
        self,
        parent,
        model_name: str,
        base_dir: str,
        tesseract_data_original_path: str,
        tesseract_data_path: str,
    ) -> None:
        super().__init__(parent)

        self.model_name = model_name
        self.base_dir = base_dir
        self.tesseract_data_original_path = tesseract_data_original_path
        self.tesseract_data_path = tesseract_data_path

        self.setWindowTitle("Image and Text Viewer")
        # screen_geometry = self.screen().geometry()
        # self.resize(screen_geometry.width(), screen_geometry.height())

        layout = QVBoxLayout()

        # Image label
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.image_label, stretch=1)

        # Index label
        self.index_label = QLabel("0 / 0")
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.index_label)

        # Grid layout for buttons and path label
        grid_layout = QVBoxLayout()

        # Text editor
        self.text_editor = CustomTextEditor(self)
        self.text_editor.ctrl_enter_pressed.connect(self.load_next)
        grid_layout.addWidget(self.text_editor)

        # Previous, Next, Remove, Train buttons
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.load_previous)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.load_next)
        button_layout.addWidget(self.next_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_current_pair)
        button_layout.addWidget(self.remove_button)

        self.train_button = QPushButton("Train")
        self.train_button.clicked.connect(self.train_model)
        button_layout.addWidget(self.train_button)

        grid_layout.addLayout(button_layout)

        layout.addLayout(grid_layout)

        self.file_base_names = self.get_file_base_names()
        self.current_index = 0

        if self.file_base_names:
            self.load_pair(self.file_base_names[self.current_index])

        self.setLayout(layout)

    def train_model(self) -> None:
        self.train_button_clicked.emit()

    def set_ground_truth_base_path(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Select Ground Truth Base Path"
        )
        if directory:
            self.base_dir = directory
            self.file_base_names = self.get_file_base_names()
            self.current_index = 0
            if self.file_base_names:
                self.load_pair(self.file_base_names[self.current_index])
            else:
                self.image_label.setText("No image loaded")
                self.text_editor.clear()

            # Update the index label
            self.index_label.setText(
                f"{self.current_index + 1} / {len(self.file_base_names)}"
            )

    def get_file_base_names(self) -> List[str]:
        file_base_paths = []
        if self.base_dir:
            for file_name in os.listdir(self.base_dir):
                if file_name.endswith(".tif"):
                    base_name = os.path.splitext(file_name)[0]
                    gt_file = os.path.join(self.base_dir, f"{base_name}.gt.txt")
                    if os.path.exists(gt_file):
                        file_base_paths.append(os.path.join(self.base_dir, base_name))
                    else:
                        raise FileNotFoundError(
                            f"Ground truth file not found for {file_name}"
                        )
                elif file_name.endswith(".gt.txt"):
                    base_name = os.path.splitext(file_name)[0]
                    base_name = base_name.replace(".gt", "")
                    image_file = os.path.join(self.base_dir, f"{base_name}.tif")
                    if not os.path.exists(image_file):
                        raise FileNotFoundError(f"Image file not found for {file_name}")
        return sorted(file_base_paths)

    def load_image(self, file_path: str) -> None:
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    pixmap.width() * 2,
                    pixmap.height() * 2,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Failed to load image")

    def load_text(self, file_path: str) -> None:
        if file_path:
            with open(file_path, "r") as file:
                text = file.read()
                self.text_editor.setText(text)
        else:
            raise ValueError(f"File path is empty: {file_path}")

    def load_pair(self, file_base_name: str) -> None:
        if file_base_name and not self.is_removed_pair(file_base_name):
            base_name = os.path.splitext(file_base_name)[0]
            image_file = f"{base_name}.tif"
            gt_file = f"{base_name}.gt.txt"

            if os.path.exists(image_file):
                self.load_image(image_file)
            else:
                raise FileNotFoundError(f"Image file not found for {file_base_name}")

            if os.path.exists(gt_file):
                self.load_text(gt_file)
            else:
                raise FileNotFoundError(
                    f"Ground truth file not found for {file_base_name}"
                )

            self.setWindowTitle(os.path.basename(image_file))

            # Update the index label
            self.index_label.setText(
                f"{self.current_index + 1} / {len(self.file_base_names)}"
            )

    def save_text(self, file_path: str) -> None:
        if file_path:
            with open(file_path, "w") as file:
                text = self.text_editor.text()
                file.write(text)
        else:
            raise ValueError(f"File path is empty: {file_path}")

    def load_previous(self) -> None:
        self.fetch_current_pair(-1)

    def load_next(self) -> None:
        self.fetch_current_pair(1)

    def fetch_current_pair(self, step: int) -> None:
        self.save_text(f"{self.file_base_names[self.current_index]}.gt.txt")

        new_index = self.current_index + step
        if 0 <= new_index < len(self.file_base_names):
            self.current_index = new_index
            self.load_pair(self.file_base_names[self.current_index])
            self.text_editor.setFocus()

    def remove_current_pair(self) -> None:
        if self.file_base_names:
            file_base_name = self.file_base_names[self.current_index]
            # Remove the files
            os.remove(f"{file_base_name}.tif")
            os.remove(f"{file_base_name}.gt.txt")

            # Log the removed pair
            self.log_removed_pair(file_base_name)

            # Update the list and load the next pair
            del self.file_base_names[self.current_index]
            if self.file_base_names:
                if self.current_index < len(self.file_base_names):
                    self.load_pair(self.file_base_names[self.current_index])
                else:
                    self.current_index = max(0, len(self.file_base_names) - 1)
                    if self.file_base_names:
                        self.load_pair(self.file_base_names[self.current_index])
            else:
                self.image_label.setText("No image loaded")
                self.text_editor.clear()

            # Update the index label
            self.index_label.setText(
                f"{self.current_index + 1} / {len(self.file_base_names)}"
            )

    def log_removed_pair(self, file_base_name: str) -> None:
        removed_pairs_file = os.path.join(self.base_dir, "removed_pairs.txt")
        if os.path.exists(removed_pairs_file):
            with open(removed_pairs_file, "r") as log_file:
                logged_pairs = log_file.read().splitlines()
        else:
            logged_pairs = []

        if file_base_name not in logged_pairs:
            with open(removed_pairs_file, "a") as log_file:
                log_file.write(f"{file_base_name}\n")

    def is_removed_pair(self, file_base_name: str) -> bool:
        removed_pairs_file = os.path.join(self.base_dir, "removed_pairs.txt")
        if os.path.exists(removed_pairs_file):
            with open(removed_pairs_file, "r") as log_file:
                logged_pairs = log_file.read().splitlines()
            return file_base_name in logged_pairs
        return False
