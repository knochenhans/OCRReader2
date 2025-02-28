import aspell  # type: ignore

from PySide6.QtCore import QObject
from .part_type import PartType
from .part_info import PartInfo


class LineBreakHelper(QObject):
    def __init__(self, lang: str) -> None:
        super().__init__()
        self.lang = lang

        self.spell = aspell.Speller("lang", self.lang)

    def merge_word(self, word: str) -> str:
        return word.replace("-\n", "")

    def check_merged_word(self, part_info: PartInfo) -> PartInfo:
        if part_info.part_type == PartType.WORD:
            merged_word = self.merge_word(part_info.unmerged_text)
            is_correct = self.spell.check(merged_word)
            return PartInfo(
                part_type=part_info.part_type,
                unmerged_text=part_info.unmerged_text,
                merged_text=merged_word,
                is_in_dictionary=is_correct,
                use_merged=is_correct,
                ocr_result_word_1=part_info.ocr_result_word_1,
                ocr_result_word_2=part_info.ocr_result_word_2,
            )
        return part_info

    def check_spelling(self, word: str) -> bool:
        return self.spell.check(word)
