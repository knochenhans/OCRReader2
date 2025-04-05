import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Type

from loguru import logger

from ocr_engine.ocr_result import (  # type: ignore
    OCRResultBlock,
)
from page.box_type import BoxType  # type: ignore


class OCRBox:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.UNKNOWN,
        order: int = 0,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.order = order
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.type: BoxType = type
        self.confidence: float = 0.0
        self.user_data: Dict = {}

        self.ocr_results: Optional[OCRResultBlock] = None
        self._callbacks: list[Callable] = []
        self._update_source: Optional[str] = None

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
        logger.debug(f"Converting OCR box {self.id} to {box_type.name}")
        new_box = BOX_TYPE_MAP[box_type.name](
            self.x, self.y, self.width, self.height, box_type
        )
        new_box.id = self.id
        new_box.order = self.order
        new_box.confidence = self.confidence
        new_box.user_data = self.user_data

        if box_type in [
            BoxType.FLOWING_IMAGE,
            BoxType.HEADING_IMAGE,
            BoxType.PULLOUT_IMAGE,
            BoxType.HORZ_LINE,
            BoxType.VERT_LINE,
        ]:
            new_box.ocr_results = None
        else:
            new_box.ocr_results = self.ocr_results
        return new_box

    def split_y(self, y: int) -> "OCRBox":
        logger.debug(f"Splitting OCR box {self.id} at y={y}")
        bottom_box = type(self)(
            self.x, y, self.width, self.y + self.height - y, self.type
        )
        bottom_box.id = str(uuid.uuid4())
        bottom_box.order = self.order + 1
        bottom_box.confidence = self.confidence
        bottom_box.user_data = self.user_data
        bottom_box.ocr_results = self.ocr_results

        self.height = y - self.y

        return bottom_box

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "position": self.position(),
            "type": self.type.name,
            "confidence": self.confidence,
            "user_data": self.user_data,
            "order": self.order,
            "ocr_results": self.ocr_results.to_dict() if self.ocr_results else None,
        }

    def add_callback(self, callback: Callable[["OCRBox"], None]) -> None:
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[["OCRBox"], None]) -> None:
        self._callbacks.remove(callback)

    def clear_callbacks(self) -> None:
        self._callbacks = []

    def notify_callbacks(self, source: Optional[str] = None) -> None:
        if source != self._update_source:
            for callback in self._callbacks:
                callback(self)

    def update_position(self, x: int, y: int, source: Optional[str] = None) -> None:
        logger.debug(
            f"Updating OCR box position: {self.id} ({self.x}, {self.y}) -> ({x}, {y})"
        )

        self.x = x
        self.y = y
        self._update_source = source
        self.notify_callbacks(source)
        self._update_source = None

    def update_size(
        self, width: int, height: int, source: Optional[str] = None
    ) -> None:
        logger.debug(
            f"Updating OCR box size: {self.id} ({self.width}, {self.height}) -> ({width}, {height})"
        )

        self.width = width
        self.height = height
        self._update_source = source
        self.notify_callbacks(source)
        self._update_source = None

    def get_image_region(self) -> Dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    def add_user_data(self, key: str, value: Any) -> None:
        self.user_data[key] = value

    def get_user_data(self, key: str) -> Any:
        return self.user_data.get(key, "")

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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
        box.ocr_results = cls.load_ocr_results(data.get("ocr_results"))
        return box

    @staticmethod
    def load_ocr_results(
        ocr_result_data: Optional[Dict],
    ) -> Optional[OCRResultBlock]:
        if not ocr_result_data:
            return None
        else:
            return OCRResultBlock.from_dict(ocr_result_data)

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
        return f"OCRBox(order={self.order}, x={self.x}, y={self.y}, width={self.width}, height={self.height}, type={self.type.name}, user_data={self.user_data}), confidence={self.confidence})"


@dataclass
class TextBox(OCRBox):
    user_text: str

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.UNKNOWN,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
        self.type = type
        self.user_text = ""
        self.flows_into_next: bool = False

    def has_text(self) -> bool:
        if not self.ocr_results:
            return False
        return len(self.get_text()) > 0

    def get_text(self) -> str:
        text = ""

        if self.ocr_results:
            text = self.ocr_results.get_text()
        return text

    def get_hocr(self) -> str:
        hocr = ""

        if self.ocr_results:
            hocr = self.ocr_results.get_hocr()
        return hocr

    def to_dict(self) -> Dict:
        return {
            **super().to_dict(),
            "user_text": self.user_text,
            "flows_into_next": self.flows_into_next,
        }

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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
        box.ocr_results = cls.load_ocr_results(data.get("ocr_results"))
        box.user_text = data.get("user_text", "")
        box.flows_into_next = data.get("flows_into_next", False)
        return box

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextBox):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        return f"TextBox(x={self.x}, y={self.y}, width={self.width}, height={self.height}, text={self.user_text})"


@dataclass
class ImageBox(OCRBox):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.UNKNOWN,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
        return box

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageBox):
            return False
        return self.to_dict() == other.to_dict()


@dataclass
class LineBox(OCRBox):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.UNKNOWN,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
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
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.EQUATION,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
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
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.TABLE,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
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
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.NOISE,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
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
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        type: BoxType = BoxType.COUNT,
        order: int = 0,
    ) -> None:
        super().__init__(x, y, width, height, type, order)
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
        box.confidence = data.get("confidence", 0.0)
        box.user_data = data.get("user_data", {})
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


# Box factory method
def create_ocr_box(
    position: Tuple[int, int, int, int], box_type: BoxType, order: int = 0
) -> OCRBox:
    x, y, width, height = position
    return BOX_TYPE_MAP[box_type.name](x, y, width, height, box_type, order)
