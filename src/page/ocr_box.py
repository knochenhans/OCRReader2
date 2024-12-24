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
    VERTICAL_TEXT = "VERTICAL_TEXT"
    CAPTION_TEXT = "CAPTION_TEXT"
    EQUATION = "EQUATION"
    INLINE_EQUATION = "INLINE_EQUATION"
    TABLE = "TABLE"
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
        type: BoxType = BoxType.UNKNOWN,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.order = 0
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.type: BoxType = type
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

    def convert_to(self, box_type: BoxType) -> "OCRBox":
        new_box = BOX_TYPE_MAP[box_type.name](
            self.x, self.y, self.width, self.height, box_type
        )
        new_box.id = self.id
        new_box.order = self.order
        new_box.class_ = self.class_
        new_box.tag = self.tag
        new_box.confidence = self.confidence
        new_box.ocr_results = self.ocr_results
        return new_box

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
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.UNKNOWN
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type
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
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.UNKNOWN
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

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
class LineBox(OCRBox):
    def __init__(
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.UNKNOWN
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["LineBox"], data: Dict) -> "LineBox":
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
        if not isinstance(other, LineBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"HorizontalLine(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


@dataclass
class EquationBox(OCRBox):
    def __init__(
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.EQUATION
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["EquationBox"], data: Dict) -> "EquationBox":
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
        if not isinstance(other, EquationBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"Equation(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


@dataclass
class TableBox(OCRBox):
    def __init__(
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.TABLE
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["TableBox"], data: Dict) -> "TableBox":
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
        if not isinstance(other, TableBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return (
            f"Table(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
        )


@dataclass
class NoiseBox(OCRBox):
    def __init__(
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.NOISE
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["NoiseBox"], data: Dict) -> "NoiseBox":
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
        if not isinstance(other, NoiseBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return (
            f"Noise(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
        )


@dataclass
class CountBox(OCRBox):
    def __init__(
        self, x: int, y: int, width: int, height: int, type: BoxType = BoxType.COUNT
    ) -> None:
        super().__init__(x, y, width, height)
        self.type = type

    def to_dict(self) -> Dict:
        return super().to_dict()

    @classmethod
    def from_dict(cls: Type["CountBox"], data: Dict) -> "CountBox":
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
        if not isinstance(other, CountBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return (
            f"Count(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
        )


BOX_TYPE_MAP = {
    "UNKNOWN": OCRBox,
    "FLOWING_TEXT": TextBox,
    "HEADING_TEXT": TextBox,
    "PULLOUT_TEXT": TextBox,
    "EQUATION": EquationBox,
    "INLINE_EQUATION": TextBox,
    "TABLE": TableBox,
    "VERTICAL_TEXT": TextBox,
    "CAPTION_TEXT": TextBox,
    "FLOWING_IMAGE": ImageBox,
    "HEADING_IMAGE": ImageBox,
    "PULLOUT_IMAGE": ImageBox,
    "HORZ_LINE": LineBox,
    "VERT_LINE": LineBox,
    "NOISE": NoiseBox,
    "COUNT": CountBox,
}
