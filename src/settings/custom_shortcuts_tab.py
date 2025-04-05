from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from page.box_type import BoxType  # type: ignore


class ShortcutsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.custom_shortcuts: Dict[str, str] = {}
        layout: QVBoxLayout = QVBoxLayout(self)

        ctrl_shortcuts_label = QLabel("Custom Tag Shortcuts")
        layout.addWidget(ctrl_shortcuts_label)

        self.ctrl_shortcuts_table: QTableWidget = QTableWidget()
        self.ctrl_shortcuts_table.setColumnCount(2)
        self.ctrl_shortcuts_table.setHorizontalHeaderLabels(["Shortcut", "Class"])
        self.ctrl_shortcuts_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.ctrl_shortcuts_table)

        for i in range(1, 10):
            row_position = self.ctrl_shortcuts_table.rowCount()
            self.ctrl_shortcuts_table.insertRow(row_position)

            shortcut_item = QTableWidgetItem(f"Ctrl + {i}")
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.ctrl_shortcuts_table.setItem(row_position, 0, shortcut_item)

            tag_item = QTableWidgetItem()
            self.ctrl_shortcuts_table.setItem(row_position, 1, tag_item)

        alt_shortcuts_label = QLabel("Box Type Shortcuts")
        layout.addWidget(alt_shortcuts_label)

        self.alt_shortcuts_table: QTableWidget = QTableWidget()
        self.alt_shortcuts_table.setColumnCount(2)
        self.alt_shortcuts_table.setHorizontalHeaderLabels(["Shortcut", "Box Type"])
        self.alt_shortcuts_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.alt_shortcuts_table)

        for i in range(1, 10):
            row_position = self.alt_shortcuts_table.rowCount()
            self.alt_shortcuts_table.insertRow(row_position)

            shortcut_item = QTableWidgetItem(f"Alt + {i}")
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.alt_shortcuts_table.setItem(row_position, 0, shortcut_item)

            box_type_combobox = QComboBox()
            box_type_combobox.addItem("")
            box_type_combobox.addItems([box_type.value for box_type in BoxType])
            self.alt_shortcuts_table.setCellWidget(row_position, 1, box_type_combobox)

    def load_custom_shortcuts(self, custom_shortcuts: Dict[str, str]) -> None:
        self.custom_shortcuts = custom_shortcuts
        for i in range(self.ctrl_shortcuts_table.rowCount()):
            ctrl_shortcut: str = self.ctrl_shortcuts_table.item(i, 0).text()
            tag: str = self.custom_shortcuts.get(ctrl_shortcut, "")
            self.ctrl_shortcuts_table.item(i, 1).setText(tag)

        for i in range(self.alt_shortcuts_table.rowCount()):
            alt_shortcut: str = self.alt_shortcuts_table.item(i, 0).text()
            box_type: str = self.custom_shortcuts.get(alt_shortcut, "")
            box_type_combobox = self.alt_shortcuts_table.cellWidget(i, 1)

            if isinstance(box_type_combobox, QComboBox):
                if box_type:
                    index = box_type_combobox.findText(box_type)
                    if index != -1:
                        box_type_combobox.setCurrentIndex(index)

    def set_custom_shortcuts(self) -> Dict[str, str]:
        for i in range(self.ctrl_shortcuts_table.rowCount()):
            ctrl_shortcut: str = self.ctrl_shortcuts_table.item(i, 0).text()
            tag: str = self.ctrl_shortcuts_table.item(i, 1).text()
            if tag:
                self.custom_shortcuts[ctrl_shortcut] = tag

        for i in range(self.alt_shortcuts_table.rowCount()):
            alt_shortcut: str = self.alt_shortcuts_table.item(i, 0).text()
            box_type_combobox = self.alt_shortcuts_table.cellWidget(i, 1)

            if isinstance(box_type_combobox, QComboBox):
                box_type: str = box_type_combobox.currentText()
                if box_type:
                    self.custom_shortcuts[alt_shortcut] = box_type

        return self.custom_shortcuts
