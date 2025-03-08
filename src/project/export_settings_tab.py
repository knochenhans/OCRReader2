from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QFormLayout

from settings import Settings  # type: ignore


class ExportSettingsTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.application_settings: Settings = Settings()
        self.init_ui()

    def init_ui(self) -> None:
        layout = QFormLayout()

        self.max_font_size_label = QLabel("Max. Font Size")
        self.max_font_size_edit = QLineEdit()
        self.max_font_size_edit.textEdited.connect(self.update_max_font_size)
        layout.addRow(self.max_font_size_label, self.max_font_size_edit)

        self.min_font_size_label = QLabel("Min. Font Size")
        self.min_font_size_edit = QLineEdit()
        self.min_font_size_edit.textEdited.connect(self.update_min_font_size)
        layout.addRow(self.min_font_size_label, self.min_font_size_edit)

        self.round_font_size_label = QLabel("Round Font Size by")
        self.round_font_size_edit = QLineEdit()
        self.round_font_size_edit.textEdited.connect(self.update_round_font_size)
        layout.addRow(self.round_font_size_label, self.round_font_size_edit)

        self.scale_factor_label = QLabel("Scale Factor")
        self.scale_factor_edit = QLineEdit()
        self.scale_factor_edit.textEdited.connect(self.update_scale_factor)
        layout.addRow(self.scale_factor_label, self.scale_factor_edit)

        self.setLayout(layout)

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings
        self.max_font_size_edit.setText(
            str(self.application_settings.get("max_font_size", 0))
        )
        self.min_font_size_edit.setText(
            str(self.application_settings.get("min_font_size", 0))
        )
        self.round_font_size_edit.setText(
            str(self.application_settings.get("round_font_size", 0))
        )
        self.scale_factor_edit.setText(
            str(self.application_settings.get("scale_factor", 0))
        )

    def update_max_font_size(self) -> None:
        self.application_settings.set(
            "max_font_size", int(self.max_font_size_edit.text())
        )

    def update_min_font_size(self) -> None:
        self.application_settings.set(
            "min_font_size", int(self.min_font_size_edit.text())
        )

    def update_round_font_size(self) -> None:
        self.application_settings.set(
            "round_font_size", int(self.round_font_size_edit.text())
        )

    def update_scale_factor(self) -> None:
        self.application_settings.set(
            "scale_factor", float(self.scale_factor_edit.text())
        )
