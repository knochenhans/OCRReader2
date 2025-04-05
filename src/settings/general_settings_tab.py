from typing import Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from PySide6.QtGui import QColor, QPalette, Qt, QFont, QIntValidator
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QColorDialog,
    QFontDialog,
)
from settings.settings import Settings  # type: ignore
from settings.settings_tab import SettingsTab, SettingType  # type: ignore


class GeneralSettingsTab(SettingsTab):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # LayoutData = Tuple[
        #     str,
        #     str,
        #     SettingType,
        #     str,
        #     Callable[[], None],
        #     Optional[QIntValidator],
        # ]

        self.settings_layouts: List = [
            (
                "OCR Editor",
                "thumbnail_size",
                SettingType.EDIT,
                "Thumbnail Size:",
                lambda: self.update_line_edit_setting("thumbnail_size"),
                QIntValidator(0, 1000, self),
            ),
            (
                "OCR Editor",
                "confidence_color_threshold",
                SettingType.EDIT,
                "Confidence Color Threshold:",
                lambda: self.update_line_edit_setting("confidence_color_threshold"),
                QIntValidator(0, 100, self),
            ),
            (
                "OCR Editor",
                "merged_word_in_dict_color",
                SettingType.COLOR,
                "Merged Word in Dictionary:",
                lambda: self.choose_color("merged_word_in_dict_color"),
                None,
            ),
            (
                "OCR Editor",
                "merged_word_not_in_dict_color",
                SettingType.COLOR,
                "Merged Word not in Dictionary:",
                lambda: self.choose_color("merged_word_not_in_dict_color"),
                None,
            ),
            (
                "OCR Editor",
                "editor_background_color",
                SettingType.COLOR,
                "Background Color:",
                lambda: self.choose_color("editor_background_color"),
                None,
            ),
            (
                "OCR Editor",
                "editor_text_color",
                SettingType.COLOR,
                "Text Color:",
                lambda: self.choose_color("editor_text_color"),
                None,
            ),
            (
                "OCR Editor",
                "editor_font",
                SettingType.FONT,
                "Font:",
                lambda: self.choose_font("editor_font"),
                None,
            ),
            (
                "Box Editor",
                "box_flow_line_color",
                SettingType.COLOR,
                "Box Flow Line Color:",
                lambda: self.choose_color("box_flow_line_color"),
                None,
            ),
            (
                "Box Editor",
                "box_item_order_font_color",
                SettingType.COLOR,
                "Box Item Order Font Color:",
                lambda: self.choose_color("box_item_order_font_color"),
                None,
            ),
            (
                "Box Editor",
                "box_item_symbol_font_color",
                SettingType.COLOR,
                "Box Item Symbol Font Color:",
                lambda: self.choose_color("box_item_symbol_font_color"),
                None,
            ),
        ]

        self.create_layout()

    def load_settings(self, application_settings: Settings) -> None:
        self.application_settings = application_settings

        self.load_line_edit_setting("thumbnail_size", 150)
        self.load_color_setting(
            "merged_word_in_dict_color", QColor(0, 255, 0, 255).rgba()
        )
        self.load_color_setting(
            "merged_word_not_in_dict_color", QColor(255, 0, 0, 255).rgba()
        )
        self.load_color_setting("box_flow_line_color", QColor(0, 0, 255, 255).rgba())
        self.load_color_setting("editor_background_color", QColor("white").rgba())
        self.load_color_setting("editor_text_color", QColor("black").rgba())
        self.load_line_edit_setting("confidence_color_threshold", 50)
        self.load_font_setting("editor_font", QFont())
        self.load_color_setting("box_item_order_font_color", QColor("green").rgba())
        self.load_color_setting("box_item_symbol_font_color", QColor("green").rgba())
