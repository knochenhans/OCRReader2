from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.setGeometry(400, 300, 400, 300)

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Project name input
        self.name_label = QLabel("Project Name:")
        self.main_layout.addWidget(self.name_label)
        self.name_input = QLineEdit(self)
        self.main_layout.addWidget(self.name_input)

        # Project description input
        self.description_label = QLabel("Project Description:")
        self.main_layout.addWidget(self.description_label)
        self.description_input = QTextEdit(self)
        self.main_layout.addWidget(self.description_input)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

    def get_project_details(self):
        return (
            self.name_input.text().strip(),
            self.description_input.toPlainText().strip(),
        )
