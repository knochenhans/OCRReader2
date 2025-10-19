from dataclasses import dataclass

from OCRReader2.ocr_edit_dialog.part_type import PartType
from OCRReader2.ocr_engine.ocr_result import OCRResultWord


@dataclass
class PartInfo:
    part_type: PartType
    unmerged_text: str
    merged_text: str
    is_in_dictionary: bool
    use_merged: bool
    ocr_result_word_1: OCRResultWord
    ocr_result_word_2: OCRResultWord
