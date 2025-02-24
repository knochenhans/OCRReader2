from enum import Enum, auto
from typing import List, Tuple
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


class LineBreakTableDialog(QDialog):
    class TokenType(Enum):
        TEXT = auto()
        SPLIT_WORD = auto()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Line Break Editor")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 3, self)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self.remove_row)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.accept_button = QPushButton("Accept")
        self.cancel_button = QPushButton("Cancel")
        self.accept_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.tokens: List[Tuple] = []

        # Hide the last column
        self.table.setColumnHidden(2, True)

    def add_tokens(self, tokens: List) -> None:
        self.tokens = tokens

        # Token = Tuple[TokenType, str, str, bool, QColor]

        for index, token in enumerate(tokens):
            if token[0].value == self.TokenType.SPLIT_WORD.value:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(token[2]))
                self.table.setItem(row_position, 1, QTableWidgetItem(token[1]))

                # Add index to the row
                item = QTableWidgetItem(str(index))
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.table.setItem(row_position, 2, item)

        self.table.resizeColumnsToContents()

    def remove_row(self, row, column):
        item = self.table.item(row, 2)

        index = item.data(Qt.ItemDataRole.UserRole)
        token = list(self.tokens[index])
        token[3] = False
        self.tokens[index] = tuple(token)
        self.table.removeRow(row)
