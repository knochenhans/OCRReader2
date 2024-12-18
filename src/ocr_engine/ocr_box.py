from dataclasses import dataclass
from typing import Dict, Union, Optional
import uuid
from src.ocr_engine.block_type import BoxType
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultLine,
    OCRResultParagraph,
    OCRResultWord,
)


class OCRBox:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.UNKNOWN,
        class_: str = "",
        tag: str = "",
        confidence: float = 0.0,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.type: BoxType = type
        self.class_: str = class_
        self.tag: str = tag
        self.confidence: float = confidence

        self.ocr_result: Optional[
            Union[OCRResultBlock, OCRResultLine, OCRResultParagraph, OCRResultWord]
        ] = None
        self.order = 0

    def position(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

    def expand(self, expansion_amount: int) -> None:
        self.x -= expansion_amount
        self.y -= expansion_amount
        self.width += 2 * expansion_amount
        self.height += 2 * expansion_amount

    def shrink(self, shrink_amount: int) -> None:
        self.x += shrink_amount
        self.y += shrink_amount
        self.width -= 2 * shrink_amount
        self.height -= 2 * shrink_amount

    def contains(self, other: "OCRBox") -> bool:
        return (
            self.x <= other.x
            and self.y <= other.y
            and self.x + self.width >= other.x + other.width
            and self.y + self.height >= other.y + other.height
        )

    def intersects(self, other: "OCRBox") -> bool:
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y
        )

    def to_dict(self) -> Dict[str, Union[str, Dict[str, int]]]:
        return {
            "id": self.id,
            "box": self.position(),
            "type": self.type.name,
            "class": self.class_,
            "tag": self.tag,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OCRBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"OCRBox(order={self.order}, x={self.x}, y={self.y}, width={self.width}, height={self.height}, type={self.type.name}, class={self.class_}, tag={self.tag})"


@dataclass
class TextBox(OCRBox):
    text: str

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        tag: str = "",
    ) -> None:
        super().__init__(x, y, width, height, BoxType.FLOWING_TEXT, tag=tag)
        self.text = text

    def to_dict(self) -> Dict[str, Union[str, Dict[str, int], str]]:
        return {**super().to_dict(), "text": self.text}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"TextBox(x={self.x}, y={self.y}, width={self.width}, height={self.height}, text={self.text})"


@dataclass
class ImageBox(OCRBox):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        super().__init__(x, y, width, height, BoxType.FLOWING_IMAGE)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageBox):
            return False
        return self.to_dict() == other.to_dict()


@dataclass
class HorizontalLine(OCRBox):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = 1,  # Typically, a horizontal line has a height of 1
        tag: str = "",
    ) -> None:
        super().__init__(x, y, width, height, BoxType.HORZ_LINE, tag=tag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HorizontalLine):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"HorizontalLine(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


@dataclass
class VerticalLine(OCRBox):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        tag: str = "",
    ) -> None:
        super().__init__(x, y, width, height, BoxType.VERT_LINE, tag=tag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VerticalLine):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"VerticalLine(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
