from typing import List, Tuple

from PySide6.QtGui import QColor


class OCRResultHelper:
    def __init__(self) -> None:
        pass

    def get_word_boxes(
        self,
        ocr_results,
        box_image_pos: Tuple[int, int],
        confidence_color_threshold: float = 75.0,
    ) -> List[Tuple[Tuple[int, int, int, int], QColor]]:
        word_boxes: List[Tuple[Tuple[int, int, int, int], QColor]] = []

        for paragraph in ocr_results.paragraphs:
            for line in paragraph.lines:
                for word in line.words:
                    if word.confidence < confidence_color_threshold:
                        if word.bbox:
                            mapped_bbox = (
                                word.bbox[0] - box_image_pos[0],
                                word.bbox[1] - box_image_pos[1],
                                word.bbox[2] - word.bbox[0],
                                word.bbox[3] - word.bbox[1],
                            )
                            word_boxes.append(
                                (
                                    mapped_bbox,
                                    word.get_confidence_color(
                                        confidence_color_threshold
                                    ),
                                )
                            )
        return word_boxes
