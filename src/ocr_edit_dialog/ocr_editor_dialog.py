from typing import List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPixmap,
    QTextCharFormat,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ocr_engine.ocr_result_helper import OCRResultHelper  # type: ignore
from ocr_engine.ocr_result_writer import OCRResultWriter  # type: ignore
from page.ocr_box import TextBox  # type: ignore
from page.page import Page  # type: ignore
from settings.settings import Settings  # type: ignore

from .clickable_text_edit import ClickableTextEdit  # type: ignore
from .image_viewer import ImageViewer  # type: ignore
from .line_break_helper import LineBreakHelper, PartInfo
from .ocr_editor_navigator import OCREditorNavigation  # type: ignore


class OCREditorDialog(QDialog):
    box_flagged_for_training = Signal(str, bool)

    def __init__(
        self,
        pages: List[Page],
        language: str,
        application_settings: Settings,
        start_box_id: str = "",
        for_project=False,
        box_ids_flagged_for_training: Optional[List[str]] = None,
    ) -> None:
        super().__init__()

        self.pages = pages
        self.language = language
        self.application_settings = application_settings
        self.training_box_ids = box_ids_flagged_for_training or []
        self.ocr_result_helper = OCRResultHelper()

        self.ocr_box: Optional[TextBox] = None

        if for_project:
            self.setWindowTitle("OCR Editor (Project)")
        else:
            self.setWindowTitle("OCR Editor")

        self.resize(1000, 600)

        # Main layout
        self.main_layout: QVBoxLayout = QVBoxLayout()

        # Horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left layout (Text Editor and Navigation Buttons)
        self.left_layout: QVBoxLayout = QVBoxLayout()

        # Text editor
        self.text_edit: ClickableTextEdit = ClickableTextEdit(self)
        if self.application_settings:
            background_color = self.application_settings.get(
                "editor_background_color", "white"
            )
            text_color = self.application_settings.get("editor_text_color", "black")
            font = self.application_settings.get("editor_font", QFont())
            self.text_edit.setStyleSheet(
                f"background-color: {QColor(background_color).name()}; color: {QColor(text_color).name()};"
            )
            self.text_edit.setFont(font)
        else:
            self.text_edit.setStyleSheet("background-color: white; color: black;")
        self.text_edit.linkRightClicked.connect(self.on_link_right_clicked)
        self.text_edit.ctrlEnterPressed.connect(self.move_forward)
        self.left_layout.addWidget(self.text_edit)

        # "Flag for Training" checkbox
        self.flag_box_training_checkbox = QCheckBox("Flag for Training", self)
        self.flag_box_training_checkbox.toggled.connect(
            self.on_box_flagged_for_training
        )
        self.left_layout.addWidget(self.flag_box_training_checkbox)

        # Navigation buttons
        self.button_layout: QHBoxLayout = QHBoxLayout()

        # Page Navigation
        self.page_left_button: QPushButton = QPushButton("<<", self)
        self.page_left_button.clicked.connect(self.previous_page)
        self.button_layout.addWidget(self.page_left_button)

        self.page_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.page_label)

        self.page_right_button: QPushButton = QPushButton(">>", self)
        self.page_right_button.clicked.connect(self.next_page)
        self.button_layout.addWidget(self.page_right_button)

        # Box Navigation
        self.left_button: QPushButton = QPushButton("<", self)
        self.left_button.clicked.connect(self.previous_box)
        self.button_layout.addWidget(self.left_button)

        self.box_label: QLabel = QLabel(self)
        self.button_layout.addWidget(self.box_label)

        self.right_button: QPushButton = QPushButton(">", self)
        self.right_button.clicked.connect(self.next_box)
        self.button_layout.addWidget(self.right_button)

        self.apply_button: QPushButton = QPushButton("Finish", self)
        self.apply_button.clicked.connect(self.apply_changes)
        self.button_layout.addWidget(self.apply_button)

        self.revert_button: QPushButton = QPushButton("Revert to OCR", self)
        self.revert_button.clicked.connect(lambda: self.set_processed_text(True))
        self.button_layout.addWidget(self.revert_button)

        self.cancel_button: QPushButton = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.left_layout.addLayout(self.button_layout)

        # Add the left layout to the splitter
        left_widget = QWidget()
        left_widget.setLayout(self.left_layout)
        splitter.addWidget(left_widget)

        # Right layout (Image)
        self.image_label = ImageViewer(self)
        self.image_label.setMinimumWidth(int(self.width() / 3))
        splitter.addWidget(self.image_label)

        # Set initial sizes for the splitter
        splitter.setSizes([600, 400])

        # Add the splitter to the main layout
        self.main_layout.addWidget(splitter)

        self.setLayout(self.main_layout)

        self.page_box_count: int = 0
        self.applied_boxes: List[bool] = []

        self.navigation = OCREditorNavigation(self.pages, self)

        if start_box_id:
            for i, (box, page_index, box_index) in enumerate(
                self.navigation.all_text_boxes
            ):
                if box.id == start_box_id:
                    first_box = box
                    self.navigation.current_page_index = page_index
                    self.navigation.current_box_index = box_index
                    self.navigation.current_absolute_box_index = i
                    self.page_box_count = len(self.pages[page_index].layout.ocr_boxes)
                    break
        else:
            first_box = self.navigation.find_next_box()

        if first_box:
            self.load_box(first_box)
        else:
            self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            event.key() == Qt.Key.Key_Right
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.next_box()
        elif (
            event.key() == Qt.Key.Key_Left
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.previous_box()
        elif (
            event.key() == Qt.Key.Key_PageUp
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.next_page()
        elif (
            event.key() == Qt.Key.Key_PageDown
            and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.previous_page()
        else:
            super().keyPressEvent(event)

    def move_forward(self) -> None:
        # Move to next box or apply changes if there are no more boxes
        if (
            self.navigation.current_absolute_box_index
            < len(self.navigation.all_text_boxes) - 1
        ):
            self.next_box()
        else:
            self.apply_changes()

    def load_box(self, box: TextBox) -> None:
        self.ocr_box = box

        self.revert_button.setEnabled(bool(self.ocr_box.ocr_results))

        self.applied_boxes = [False] * self.page_box_count

        self.line_break_helper: LineBreakHelper = LineBreakHelper(self.language)

        self.update_navigation_labels()
        self.set_processed_text()

        image_path = self.pages[self.navigation.current_page_index].image_path

        if not self.ocr_box:
            return

        ocr_results = self.ocr_box.ocr_results

        if not ocr_results:
            return

        confidence_color_threshold = self.application_settings.get(
            "confidence_color_threshold", 75.0
        )

        image_region = self.ocr_box.get_image_region()

        if image_path:
            image = QPixmap(image_path)
            image = image.copy(
                image_region["x"],
                image_region["y"],
                image_region["width"],
                image_region["height"],
            )
            self.image_label.add_pixmaps([image])

        word_boxes = self.ocr_result_helper.get_word_boxes(
            ocr_results,
            (image_region["x"], image_region["y"]),
            confidence_color_threshold,
        )

        self.image_label.add_boxes(word_boxes, 0)

        # Enable or disable the checkbox based on the box ID
        self.flag_box_training_checkbox.setChecked(
            self.ocr_box.id in self.training_box_ids
        )

    def update_navigation_labels(self) -> None:
        self.box_label.setText(
            f"Block {self.navigation.current_box_index + 1} of {self.page_box_count}"
        )
        self.page_label.setText(
            f"Page {self.navigation.current_page_index + 1} of {len(self.pages)}"
        )

    def set_processed_text(self, revert=False) -> None:
        if not self.ocr_box:
            return

        if revert or not self.ocr_box.user_text.strip():
            ocr_result_writer = OCRResultWriter(
                self.application_settings, self.language
            )

            if not self.ocr_box.ocr_results:
                return

            self.text_edit.setDocument(
                ocr_result_writer.to_qdocument([self.ocr_box.ocr_results])
            )
        else:
            self.text_edit.clear()
            self.text_edit.setCurrentCharFormat(QTextCharFormat())
            self.text_edit.setPlainText(self.ocr_box.user_text)

    @Slot()
    def next_box(self) -> None:
        self.navigation.next_box()

    @Slot()
    def previous_box(self) -> None:
        self.navigation.previous_box()

    @Slot()
    def next_page(self) -> None:
        self.navigation.next_page()

    @Slot()
    def previous_page(self) -> None:
        self.navigation.previous_page()

    def update_navigation_buttons(self) -> None:
        self.left_button.setEnabled(self.navigation.current_absolute_box_index > 0)
        self.right_button.setEnabled(
            self.navigation.current_absolute_box_index
            < len(self.navigation.all_text_boxes) - 1
        )

        self.page_left_button.setEnabled(self.navigation.current_page_index > 0)
        self.page_right_button.setEnabled(
            self.navigation.current_page_index < len(self.pages) - 1
        )

    @Slot(str)
    def on_link_right_clicked(self, url: str) -> None:
        # if url.startswith("spell:"):
        #     index = int(url.split(":")[1])

        #     if index < len(self.current_parts):
        #         part_info = self.current_parts[index]
        #         self.current_parts[index] = PartInfo(
        #             part_type=part_info.part_type,
        #             unmerged_text=part_info.unmerged_text,
        #             merged_text=part_info.merged_text,
        #             is_in_dictionary=part_info.is_in_dictionary,
        #             use_merged=not part_info.use_merged,
        #             ocr_result_word_1=part_info.ocr_result_word_1,
        #             ocr_result_word_2=part_info.ocr_result_word_2,
        #         )

        #         self.update_editor_text()
        pass

    @Slot()
    def apply_changes(self) -> None:
        self.update_block_user_text()
        self.accept()

    def update_block_user_text(self) -> None:
        if self.ocr_box:
            self.ocr_box.user_text = self.get_text().strip()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    @Slot(bool)
    def on_box_flagged_for_training(self, checked: bool) -> None:
        if self.ocr_box:
            self.box_flagged_for_training.emit(self.ocr_box.id, checked)
