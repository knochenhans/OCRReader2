from dataclasses import dataclass
from enum import Enum
from typing import Dict, Type, Union, Optional
import uuid
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultLine,
    OCRResultParagraph,
    OCRResultWord,
)


class BoxType(Enum):
    UNKNOWN = "UNKNOWN"
    FLOWING_TEXT = "FLOWING_TEXT"
    HEADING_TEXT = "HEADING_TEXT"
    PULLOUT_TEXT = "PULLOUT_TEXT"
    EQUATION = "EQUATION"
    INLINE_EQUATION = "INLINE_EQUATION"
    TABLE = "TABLE"
    VERTICAL_TEXT = "VERTICAL_TEXT"
    CAPTION_TEXT = "CAPTION_TEXT"
    FLOWING_IMAGE = "FLOWING_IMAGE"
    HEADING_IMAGE = "HEADING_IMAGE"
    PULLOUT_IMAGE = "PULLOUT_IMAGE"
    HORZ_LINE = "HORZ_LINE"
    VERT_LINE = "VERT_LINE"
    NOISE = "NOISE"
    COUNT = "COUNT"


class OCRBox:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.order = 0
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.type: BoxType = BoxType.UNKNOWN
        self.class_: str = ""
        self.tag: str = ""
        self.confidence: float = 0.0

        self.ocr_results: Optional[
            Union[OCRResultBlock, OCRResultLine, OCRResultParagraph, OCRResultWord]
        ] = None

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

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "position": self.position(),
            "type": self.type.name,
            "class": self.class_,
            "tag": self.tag,
            "confidence": self.confidence,
            "order": self.order,
            "ocr_results": self.ocr_results.to_dict() if self.ocr_results else None,
        }

    @classmethod
    def from_dict(cls: Type["OCRBox"], data: Dict) -> "OCRBox":
        position_data = data["position"]
        box = cls(
            x=position_data["x"],
            y=position_data["y"],
            width=position_data["width"],
            height=position_data["height"],
        )
        box.id = data["id"]
        box.order = data.get("order", 0)
        box.type = BoxType[data["type"]]
        box.class_ = data.get("class", "")
        box.tag = data.get("tag", "")
        box.confidence = data.get("confidence", 0.0)
        box.ocr_results = cls.load_ocr_results(data.get("ocr_results"))
        return box

    @staticmethod
    def load_ocr_results(
        ocr_result_data: Optional[Dict],
    ) -> Optional[
        Union[OCRResultBlock, OCRResultLine, OCRResultParagraph, OCRResultWord]
    ]:
        if not ocr_result_data:
            return None
        if ocr_result_data["type"] == "block":
            return OCRResultBlock.from_dict(ocr_result_data)
        elif ocr_result_data["type"] == "paragraph":
            return OCRResultLine.from_dict(ocr_result_data)
        elif ocr_result_data["type"] == "line":
            return OCRResultParagraph.from_dict(ocr_result_data)
        elif ocr_result_data["type"] == "word":
            return OCRResultWord.from_dict(ocr_result_data)
        return None

    def similarity(self, other: "OCRBox") -> float:
        return 1.0 - (
            abs(self.x - other.x)
            + abs(self.y - other.y)
            + abs(self.width - other.width)
            + abs(self.height - other.height)
        ) / (self.width + self.height)

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
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = BoxType.FLOWING_TEXT
        self.text = ""

    def to_dict(self) -> Dict:
        return {**super().to_dict(), "text": self.text}

    @classmethod
    def from_dict(cls: Type["TextBox"], data: Dict) -> "TextBox":
        position_data = data["position"]
        box = cls(
            x=position_data["x"],
            y=position_data["y"],
            width=position_data["width"],
            height=position_data["height"],
        )
        box.id = data["id"]
        box.order = data.get("order", 0)
        box.type = BoxType[data["type"]]
        box.class_ = data.get("class", "")
        box.tag = data.get("tag", "")
        box.confidence = data.get("confidence", 0.0)
        box.ocr_results = cls.load_ocr_results(data.get("ocr_results"))
        box.text = data.get("text", "")
        return box

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
        super().__init__(x, y, width, height)
        self.type = BoxType.FLOWING_IMAGE

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["ImageBox"], data: Dict) -> "ImageBox":
        ocr_box = super().from_dict(data)
        box = cls(
            x=ocr_box.x,
            y=ocr_box.y,
            width=ocr_box.width,
            height=ocr_box.height,
        )
        box.ocr_results = data.get("ocr_results")
        box.id = data["id"]
        box.order = data.get("order", 0)
        box.type = BoxType[data["type"]]
        box.class_ = data.get("class", "")
        box.tag = data.get("tag", "")
        box.confidence = data.get("confidence", 0.0)
        return box

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
        height: int,
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = BoxType.HORZ_LINE

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["HorizontalLine"], data: Dict) -> "HorizontalLine":
        ocr_box = super().from_dict(data)
        box = cls(
            x=ocr_box.x,
            y=ocr_box.y,
            width=ocr_box.width,
            height=ocr_box.height,
        )
        box.ocr_results = data.get("ocr_results")
        box.id = data["id"]
        box.order = data.get("order", 0)
        box.type = BoxType[data["type"]]
        box.class_ = data.get("class", "")
        box.tag = data.get("tag", "")
        box.confidence = data.get("confidence", 0.0)
        return box

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
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = BoxType.VERT_LINE

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["VerticalLine"], data: Dict) -> "VerticalLine":
        ocr_box = super().from_dict(data)
        box = cls(
            x=ocr_box.x,
            y=ocr_box.y,
            width=ocr_box.width,
            height=ocr_box.height,
        )
        box.ocr_results = data.get("ocr_results")
        box.id = data["id"]
        box.order = data.get("order", 0)
        box.type = BoxType[data["type"]]
        box.class_ = data.get("class", "")
        box.tag = data.get("tag", "")
        box.confidence = data.get("confidence", 0.0)
        return box

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VerticalLine):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"VerticalLine(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


BOX_TYPE_MAP = {
    "UNKNOWN": OCRBox,
    "FLOWING_TEXT": TextBox,
    "HEADING_TEXT": TextBox,
    "PULLOUT_TEXT": TextBox,
    "EQUATION": TextBox,
    "INLINE_EQUATION": TextBox,
    "TABLE": TextBox,
    "VERTICAL_TEXT": TextBox,
    "CAPTION_TEXT": TextBox,
    "FLOWING_IMAGE": ImageBox,
    "HEADING_IMAGE": ImageBox,
    "PULLOUT_IMAGE": ImageBox,
    "HORZ_LINE": HorizontalLine,
    "VERT_LINE": VerticalLine,
    "NOISE": OCRBox,
    "COUNT": OCRBox,
}
