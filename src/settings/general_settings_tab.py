from typing import List

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget

from settings.settings import Settings  # type: ignore
from settings.settings_tab import (  # type: ignore
    SettingLayout,
    SettingsTab,
    SettingType,
)


class GeneralSettingsTab(SettingsTab):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.settings_layouts: List[SettingLayout] = [
            SettingLayout(
                category="OCR Editor",
                key="thumbnail_size",
                setting_type=SettingType.SPINBOX_INT,
                label="Thumbnail Size:",
                action=lambda: self.update_spinbox_int_setting("thumbnail_size"),
                data_type=int,
                bottom=0,
                top=1000,
            ),
            SettingLayout(
                category="OCR Editor",
                key="confidence_color_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="Confidence Color Threshold:",
                action=lambda: self.update_spinbox_int_setting(
                    "confidence_color_threshold"
                ),
                data_type=int,
                bottom=0,
                top=100,
            ),
            SettingLayout(
                category="OCR Editor",
                key="merged_word_in_dict_color",
                setting_type=SettingType.COLOR,
                label="Merged Word in Dictionary:",
                action=lambda: self.choose_color("merged_word_in_dict_color"),
            ),
            SettingLayout(
                category="OCR Editor",
                key="merged_word_not_in_dict_color",
                setting_type=SettingType.COLOR,
                label="Merged Word not in Dictionary:",
                action=lambda: self.choose_color("merged_word_not_in_dict_color"),
            ),
            SettingLayout(
                category="OCR Editor",
                key="editor_background_color",
                setting_type=SettingType.COLOR,
                label="Background Color:",
                action=lambda: self.choose_color("editor_background_color"),
            ),
            SettingLayout(
                category="OCR Editor",
                key="editor_text_color",
                setting_type=SettingType.COLOR,
                label="Text Color:",
                action=lambda: self.choose_color("editor_text_color"),
            ),
            SettingLayout(
                category="OCR Editor",
                key="editor_font",
                setting_type=SettingType.FONT,
                label="Font:",
                action=lambda: self.choose_font("editor_font"),
            ),
            SettingLayout(
                category="Box Editor",
                key="box_flow_line_color",
                setting_type=SettingType.COLOR,
                label="Box Flow Line Color:",
                action=lambda: self.choose_color("box_flow_line_color"),
            ),
            SettingLayout(
                category="Box Editor",
                key="box_item_order_font_color",
                setting_type=SettingType.COLOR,
                label="Box Item Order Font Color:",
                action=lambda: self.choose_color("box_item_order_font_color"),
            ),
            SettingLayout(
                category="Box Editor",
                key="box_item_symbol_font_color",
                setting_type=SettingType.COLOR,
                label="Box Item Symbol Font Color:",
                action=lambda: self.choose_color("box_item_symbol_font_color"),
            ),
            SettingLayout(
                category="Training",
                key="max_training_lines",
                setting_type=SettingType.SPINBOX_INT,
                label="Max Training Lines:",
                action=lambda: self.update_spinbox_int_setting("max_training_lines"),
                data_type=int,
                bottom=0,
                top=100,
            ),
            SettingLayout(
                category="Training",
                key="training_line_confidence_threshold",
                setting_type=SettingType.SPINBOX_INT,
                label="Training Line Confidence Threshold:",
                action=lambda: self.update_spinbox_int_setting(
                    "training_line_confidence_threshold"
                ),
                data_type=int,
                bottom=0,
                top=100,
            ),
            SettingLayout(
                category="Training",
                key="remove_training_lines_before_training",
                setting_type=SettingType.CHECKBOX,
                label="Remove Training Lines Before Training:",
                action=lambda: self.update_checkbox_setting(
                    "remove_training_lines_before_training"
                ),
                data_type=bool,
            ),
            SettingLayout(
                category="Training",
                key="training_iterations",
                setting_type=SettingType.SPINBOX_INT,
                label="Training Iterations:",
                action=lambda: self.update_spinbox_int_setting("training_iterations"),
                data_type=int,
                bottom=1,
                top=1000,
            ),
        ]

        self.create_layout()

    def load_settings(self, application_settings: Settings) -> None:
        self.settings = application_settings

        # Load SPINBOX_INT settings
        self.load_spinbox_int_setting("thumbnail_size", 150)
        self.load_spinbox_int_setting("confidence_color_threshold", 50)
        self.load_spinbox_int_setting("max_training_lines", 100)
        self.load_spinbox_int_setting("training_line_confidence_threshold", 90)

        # Load COLOR settings
        self.load_color_setting(
            "merged_word_in_dict_color", QColor(0, 255, 0, 255).rgba()
        )
        self.load_color_setting(
            "merged_word_not_in_dict_color", QColor(255, 0, 0, 255).rgba()
        )
        self.load_color_setting("box_flow_line_color", QColor(0, 0, 255, 255).rgba())
        self.load_color_setting("editor_background_color", QColor("white").rgba())
        self.load_color_setting("editor_text_color", QColor("black").rgba())
        self.load_color_setting("box_item_order_font_color", QColor("green").rgba())
        self.load_color_setting("box_item_symbol_font_color", QColor("green").rgba())

        # Load FONT settings
        self.load_font_setting("editor_font", QFont())

        # Load CHECKBOX settings
        self.load_checkbox_setting("remove_training_lines_before_training", True)
