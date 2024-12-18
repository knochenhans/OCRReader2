from typing import List

from src.ocr_engine.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR
from src.ocr_engine.ocr_box import OCRBox


class PageLayout:
    def __init__(self, boxes: List[OCRBox]) -> None:
        self.boxes = boxes

    def sort_boxes(self) -> None:
        self.boxes.sort(key=lambda box: box.order)
        self.update_order()

    def update_order(self) -> None:
        for index, box in enumerate(self.boxes):
            box.order = index

    def move_box(self, index: int, new_index: int) -> None:
        box_to_move = self.boxes.pop(index)
        self.boxes.insert(new_index, box_to_move)
        self.update_order()

    def remove_box(self, index: int) -> None:
        self.boxes.pop(index)
        self.update_order()

    def add_box(self, box: OCRBox, index: int) -> None:
        self.boxes.insert(index, box)
        self.update_order()

    def get_box(self, index: int) -> OCRBox:
        return self.boxes[index]

    def analyze_layout(self, image_path: str, ppi: int, langs: List[str]) -> None:
        layout_analyzer = LayoutAnalyzerTesserOCR(langs)
        self.boxes = layout_analyzer.analyze_layout(image_path, ppi)

    def __len__(self) -> int:
        return len(self.boxes)

    def __iter__(self):
        return iter(self.boxes)

    def __getitem__(self, index: int) -> OCRBox:
        return self.boxes[index]

    def __setitem__(self, index: int, box: OCRBox) -> None:
        self.boxes[index] = box

    def __delitem__(self, index: int) -> None:
        self.boxes.pop(index)

    def __str__(self) -> str:
        return f"PageLayout(boxes={self.boxes})"

    def __repr__(self) -> str:
        return self.__str__()
