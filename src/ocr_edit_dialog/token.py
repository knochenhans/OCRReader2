from dataclasses import dataclass
from enum import Enum
from PySide6.QtGui import QColor


@dataclass
class Token:
    token_type: Enum
    text: str
    unmerged_text: str
    is_split_word: bool
    color: QColor
