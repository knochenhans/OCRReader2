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
from .token import Token
from .token_type import TokenType


class LineBreakTableDialog(QDialog):
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

        self.tokens: List[Token] = []

        # Hide the last column
        self.table.setColumnHidden(2, True)

    def add_tokens(self, tokens: List[Token]) -> None:
        self.tokens = tokens

        for index, token in enumerate(tokens):
            if token.token_type == TokenType.SPLIT_WORD:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(token.unmerged_text))
                self.table.setItem(
                    row_position, 1, QTableWidgetItem(token.text)
                )

                # Add index to the row
                item = QTableWidgetItem(str(index))
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.table.setItem(row_position, 2, item)

        self.table.resizeColumnsToContents()

    def remove_row(self, row, column) -> None:
        item = self.table.item(row, 2)

        index = item.data(Qt.ItemDataRole.UserRole)
        token: Token = self.tokens[index]
        token.is_split_word = (
            False  # Assuming 'is_active' is the correct attribute to modify
        )
        self.tokens[index] = token
        self.table.removeRow(row)
