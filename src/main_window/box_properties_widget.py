from typing import List, Optional

from loguru import logger
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from page.box_type import BoxType  # type: ignore
from page.ocr_box import OCRBox, TextBox  # type: ignore


class UserDataTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.viewport().installEventFilter(self)

    def add_row(self, row: int, column: int) -> None:
        self.insertRow(row + 1)
        self.setItem(row + 1, 0, QTableWidgetItem(""))
        self.setItem(row + 1, 1, QTableWidgetItem(""))

    def eventFilter(self, source, event) -> bool:
        if (
            event.type() == QEvent.Type.MouseButtonDblClick
            and source is self.viewport()
        ):
            index = self.indexAt(event.pos())
            if index.isValid():
                self.edit(index)
            else:
                self.insertRow(self.rowCount())
            return True
        return super().eventFilter(source, event)


class BoxPropertiesWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.current_box: Optional[OCRBox] = None
        self.boxes: Optional[List[OCRBox]] = None
        self.current_index: int = 0

        # Create form layout
        self.form_layout = QFormLayout()

        # Create labels and line edits for each property
        self.id_label = QLabel("ID:")
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)

        self.order_label = QLabel("Order:")
        self.order_edit = QLineEdit()
        self.order_edit.editingFinished.connect(self.update_order)

        # Create a horizontal layout for position and size
        self.position_size_layout = QHBoxLayout()

        self.x_label = QLabel("X:")
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 10000)
        self.x_spinbox.valueChanged.connect(self.update_x)

        self.y_label = QLabel("Y:")
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 10000)
        self.y_spinbox.valueChanged.connect(self.update_y)

        self.width_label = QLabel("W:")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(0, 10000)
        self.width_spinbox.valueChanged.connect(self.update_width)

        self.height_label = QLabel("H:")
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(0, 10000)
        self.height_spinbox.valueChanged.connect(self.update_height)

        # Add position and size widgets to the horizontal layout
        self.position_size_layout.addWidget(self.x_label)
        self.position_size_layout.addWidget(self.x_spinbox)
        self.position_size_layout.addWidget(self.y_label)
        self.position_size_layout.addWidget(self.y_spinbox)
        self.position_size_layout.addWidget(self.width_label)
        self.position_size_layout.addWidget(self.width_spinbox)
        self.position_size_layout.addWidget(self.height_label)
        self.position_size_layout.addWidget(self.height_spinbox)

        self.type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems([box_type.name for box_type in BoxType])
        self.type_combo.currentTextChanged.connect(self.update_type)

        self.confidence_label = QLabel("Confidence:")
        self.confidence_edit = QLineEdit()
        self.confidence_edit.setReadOnly(True)

        self.user_text_label = QLabel("User text:")
        self.user_text_edit = QTextEdit()
        self.user_text_edit.setPlaceholderText("Empty User Text")
        self.user_text_edit.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.user_text_edit.textChanged.connect(self.update_user_text)
        self.user_text_edit.hide()

        self.user_data_table = UserDataTable()

        # Add widgets to form layout
        self.form_layout.addRow(self.id_label, self.id_edit)
        self.form_layout.addRow(self.order_label, self.order_edit)
        self.form_layout.addRow(self.position_size_layout)
        self.form_layout.addRow(self.type_label, self.type_combo)
        self.form_layout.addRow(self.confidence_label, self.confidence_edit)
        self.form_layout.addRow(self.user_text_label, self.user_text_edit)
        self.form_layout.addRow(self.user_data_table)

        # Create navigation buttons
        # self.navigation_layout = QHBoxLayout()
        # self.prev_button = QPushButton("<")
        # self.prev_button.clicked.connect(self.show_prev_box)
        # self.next_button = QPushButton(">")
        # self.next_button.clicked.connect(self.show_next_box)
        # self.navigation_layout.addWidget(self.prev_button)
        # self.navigation_layout.addWidget(self.next_button)

        # Set the widget layout
        self.box_layout = QVBoxLayout()
        self.box_layout.addLayout(self.form_layout)
        # self.box_layout.addLayout(self.navigation_layout)
        self.setLayout(self.box_layout)
        self.hide()

    def show_prev_box(self) -> None:
        if self.boxes and self.current_index > 0:
            self.current_index -= 1
            self.set_box([self.boxes[self.current_index]])

    def show_next_box(self) -> None:
        if self.boxes and self.current_index < len(self.boxes) - 1:
            self.current_index += 1
            self.set_box([self.boxes[self.current_index]])

    def set_box(self, boxes: Optional[List[OCRBox]] = None) -> None:
        if boxes:
            self.show()
        else:
            self.hide()
            return

        box = boxes[0]

        if not box:
            logger.error("No box to display")
            return

        self.current_box = box
        self.id_edit.setText(box.id)
        self.order_edit.setText(str(box.order))
        self.x_spinbox.setValue(box.x)
        self.y_spinbox.setValue(box.y)
        self.width_spinbox.setValue(box.width)
        self.height_spinbox.setValue(box.height)
        self.type_combo.setCurrentText(box.type.name)
        self.confidence_edit.setText(str(box.confidence))

        if isinstance(box, TextBox):
            self.user_text_edit.show()
            self.user_text_edit.setText(box.user_text)
        else:
            self.user_text_edit.hide()

        # Update user data table
        self.user_data_table.setRowCount(len(box.user_data))
        for row, (key, value) in enumerate(box.user_data.items()):
            key_item = QTableWidgetItem(key)
            key_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Make key read-only
            value_item = QTableWidgetItem(value)
            self.user_data_table.setItem(row, 0, key_item)
            self.user_data_table.setItem(row, 1, value_item)

    def update_order(self) -> None:
        if self.current_box:
            self.current_box.order = int(self.order_edit.text())

    def update_x(self) -> None:
        if self.current_box:
            self.current_box.x = self.x_spinbox.value()

    def update_y(self) -> None:
        if self.current_box:
            self.current_box.y = self.y_spinbox.value()

    def update_width(self) -> None:
        if self.current_box:
            self.current_box.width = self.width_spinbox.value()

    def update_height(self) -> None:
        if self.current_box:
            self.current_box.height = self.height_spinbox.value()

    def update_type(self) -> None:
        if self.current_box:
            self.current_box.type = BoxType[self.type_combo.currentText()]

    def update_user_text(self) -> None:
        if self.current_box and isinstance(self.current_box, TextBox):
            self.current_box.user_text = self.user_text_edit.toPlainText()
