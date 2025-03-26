from typing import List, Optional

from loguru import logger

from page.ocr_box import OCRBox, create_ocr_box  # type: ignore
from page.box_type import BoxType  # type: ignore


class PageLayout:
    def __init__(self, ocr_boxes: List[OCRBox]) -> None:
        self.ocr_boxes: List[OCRBox] = ocr_boxes
        self.region: tuple = (0, 0, 0, 0)  # (x, y, width, height)
        self.header_y: int = 0
        self.footer_y: int = 0

    def get_page_region(self) -> tuple:
        footer_y = self.footer_y if self.footer_y > 0 else self.region[3]
        return (self.region[0], self.header_y, self.region[2], footer_y - self.header_y)

    def sort_ocr_boxes_by_order(self) -> None:
        self.ocr_boxes.sort(key=lambda box: box.order)
        self.update_order()

    def update_order(self) -> None:
        for index, box in enumerate(self.ocr_boxes):
            box.order = index

    def change_box_index(self, index: int, new_index: int) -> None:
        box_to_move = self.ocr_boxes.pop(index)
        self.ocr_boxes.insert(new_index, box_to_move)
        self.update_order()

    def remove_ocr_box(self, index: int) -> None:
        self.ocr_boxes.pop(index)
        self.update_order()

    def remove_ocr_box_by_id(self, box_id: str) -> None:
        for index, box in enumerate(self.ocr_boxes):
            if box.id == box_id:
                self.remove_ocr_box(index)
                return

    def add_ocr_box(self, box: OCRBox, index: Optional[int] = None) -> None:
        if index is None:
            self.ocr_boxes.append(box)
        else:
            self.ocr_boxes.insert(index, box)
        self.update_order()

    def add_new_ocr_box(
        self,
        region: tuple[int, int, int, int],
        box_type: BoxType,
        index: Optional[int] = None,
        box_id: Optional[str] = None,
    ) -> OCRBox:
        ocr_box = create_ocr_box(region, box_type)
        if box_id:
            ocr_box.id = box_id
        self.add_ocr_box(ocr_box, index)
        return ocr_box

    def get_ocr_box(self, index: int) -> OCRBox:
        return self.ocr_boxes[index]

    def get_ocr_box_by_id(self, box_id: str) -> Optional[OCRBox]:
        for box in self.ocr_boxes:
            if box.id == box_id:
                return box
        return None

    def get_ocr_box_index_by_id(self, box_id: str) -> Optional[int]:
        for index, box in enumerate(self.ocr_boxes):
            if box.id == box_id:
                return index
        return None

    def replace_ocr_box(self, index: int, box: OCRBox) -> None:
        self.ocr_boxes[index] = box

    def replace_ocr_box_by_id(self, box_id: str, box: OCRBox) -> None:
        for index, ocr_box in enumerate(self.ocr_boxes):
            if ocr_box.id == box_id:
                self.ocr_boxes[index] = box
                return

    def split_y_ocr_box(self, box_id: str, split_y: int) -> Optional["OCRBox"]:
        ocr_box = self.get_ocr_box_by_id(box_id)
        if ocr_box:
            bottom_box = ocr_box.split_y(split_y)
            box_index = self.get_ocr_box_index_by_id(box_id)
            if box_index is not None:
                bottom_box_index = box_index + 1
                self.add_ocr_box(bottom_box, bottom_box_index)
            return bottom_box
        return None
    
    def clear_ocr_boxes(self) -> None:
        self.ocr_boxes.clear()

    def to_dict(self) -> dict:
        return {
            "boxes": [box.to_dict() for box in self.ocr_boxes],
            "region": self.region,
            "header_y": self.header_y,
            "footer_y": self.footer_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PageLayout":
        layout = cls([])
        layout.region = data.get("region", (0, 0, 0, 0))
        layout.header_y = data.get("header_y", 0)
        layout.footer_y = data.get("footer_y", 0)
        layout.ocr_boxes = [
            OCRBox.from_dict(box_data) for box_data in data.get("boxes", [])
        ]
        return layout

    def __len__(self) -> int:
        return len(self.ocr_boxes)

    def __iter__(self):
        return iter(self.ocr_boxes)

    def __getitem__(self, index: int) -> OCRBox:
        return self.ocr_boxes[index]

    def __setitem__(self, index: int, box: OCRBox) -> None:
        self.ocr_boxes[index] = box

    def __delitem__(self, index: int) -> None:
        self.ocr_boxes.pop(index)

    def __str__(self) -> str:
        return f"PageLayout(boxes={self.ocr_boxes})"

    def __repr__(self) -> str:
        return self.__str__()
