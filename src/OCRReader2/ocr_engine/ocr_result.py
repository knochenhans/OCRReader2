from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from tesserocr import Justification

# Define a specific type for the bounding box
BoundingBox = Tuple[int, int, int, int]  # (x, y, width, height)


class OCRResultElement(ABC):
    def __init__(self) -> None:
        self.bbox: Optional[BoundingBox] = None
        self.confidence: float = 0.0

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_hocr(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    def get_confidence_color(self, threshold: float = 0.0) -> Tuple[int, int, int, int]:
        if self.confidence <= threshold:
            return (255, 0, 0, int(255 * (1 - (self.confidence / 100))))
        return (0, 0, 0, 0)

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultElement":
        pass


class OCRResultBlock(OCRResultElement):
    def __init__(self) -> None:
        self.paragraphs: List[OCRResultParagraph] = []
        self.language: str = ""

    def add_paragraph(self, paragraph: "OCRResultParagraph") -> None:
        self.paragraphs.append(paragraph)

    def get_text(self) -> str:
        return "\n".join([paragraph.get_text() for paragraph in self.paragraphs])

    def get_hocr(self) -> str:
        paragraphs = "\n".join([paragraph.get_hocr() for paragraph in self.paragraphs])

        if self.bbox is not None:
            return f'<div class="ocrx_block" title="bbox {self.bbox[0]} {self.bbox[1]} {self.bbox[0] + self.bbox[2]} {self.bbox[1] + self.bbox[3]}; x_wconf {self.confidence}">{paragraphs}</div>'
        return self.get_text()

    def get_confidence_html(self) -> str:
        paragraphs = "\n".join(
            [paragraph.get_confidence_html() for paragraph in self.paragraphs]
        )
        return paragraphs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "block",
            "bbox": self.bbox,
            "confidence": self.confidence,
            "paragraphs": [paragraph.to_dict() for paragraph in self.paragraphs],
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultBlock":
        instance = cls()
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        instance.paragraphs = [
            OCRResultParagraph.from_dict(p) for p in data.get("paragraphs", [])
        ]
        instance.language = data.get("language", "")
        return instance

    def __repr__(self) -> str:
        return f"OCRResultBlock(paragraphs={self.paragraphs}, bbox={self.bbox}, confidence={self.confidence}, language={self.language})"


class OCRResultParagraph(OCRResultElement):
    def __init__(self) -> None:
        self.first_line_indent: bool = False
        self.is_crown: bool = False
        self.is_list_item: bool = False
        self.justification: Optional[Justification] = None
        self.lines: List[OCRResultLine] = []
        self.user_text: str = ""

    def add_line(self, line: "OCRResultLine") -> None:
        self.lines.append(line)

    def get_text(self) -> str:
        if self.user_text:
            return self.user_text
        return "\n".join([line.get_text() for line in self.lines])

    def get_hocr(self) -> str:
        lines = " ".join([line.get_hocr() for line in self.lines])

        if self.bbox is not None:
            return f'<span class="ocr_par" title="bbox {self.bbox[0]} {self.bbox[1]} {self.bbox[0] + self.bbox[2]} {self.bbox[1] + self.bbox[3]}; x_wconf {self.confidence}">{lines}</span>'
        return self.get_text()

    def get_confidence_html(self) -> str:
        lines = "\n".join([line.get_confidence_html() for line in self.lines])
        return lines

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paragraph",
            "bbox": self.bbox,
            "confidence": self.confidence,
            "lines": [line.to_dict() for line in self.lines],
            "user_text": self.user_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultParagraph":
        instance = cls()
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        instance.lines = [
            OCRResultLine.from_dict(line) for line in data.get("lines", [])
        ]
        instance.user_text = data.get("user_text", "")
        return instance

    def __repr__(self) -> str:
        return f"OCRResultParagraph(lines={self.lines})"


class OCRResultLine(OCRResultElement):
    def __init__(self) -> None:
        self.baseline: Optional[tuple[tuple[int, int], tuple[int, int]]] = None
        self.words: List[OCRResultWord] = []

    def add_word(self, word: "OCRResultWord") -> None:
        self.words.append(word)

    def get_text(self) -> str:
        return " ".join([word.get_text() for word in self.words])

    def get_hocr(self) -> str:
        words = " ".join([word.get_hocr() for word in self.words])

        if self.bbox is not None:
            return f'<span class="ocrx_line" title="bbox {self.bbox[0]} {self.bbox[1]} {self.bbox[0] + self.bbox[2]} {self.bbox[1] + self.bbox[3]}; x_wconf {self.confidence}">{words}</span>'
        return self.get_text()

    def get_confidence_html(self) -> str:
        words = " ".join([word.get_confidence_html() for word in self.words])
        return words

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "line",
            "bbox": self.bbox,
            "confidence": self.confidence,
            "baseline": self.baseline,
            "words": [word.to_dict() for word in self.words],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultLine":
        instance = cls()
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        baseline = data.get("baseline", [])  # tuple[tuple[int, int], tuple[int, int]]
        if baseline:
            start, end = baseline
            instance.baseline = (tuple(start), tuple(end))
        instance.words = [OCRResultWord.from_dict(w) for w in data.get("words", [])]
        return instance

    def __repr__(self) -> str:
        return f"OCRResultLine(words={self.words})"


class OCRResultWord(OCRResultElement):
    def __init__(self) -> None:
        self.text: str = ""
        self.word_font_attributes: Dict[str, Any] = {}
        self.word_recognition_language: str = ""
        self.symbols: List[OCRResultSymbol] = []

    def add_symbol(self, symbol: "OCRResultSymbol") -> None:
        self.symbols.append(symbol)

    def get_text(self) -> str:
        if self.symbols:
            return "".join([symbol.get_text() for symbol in self.symbols])
        return self.text

    def get_hocr(self) -> str:
        symbols = "".join([symbol.get_hocr() for symbol in self.symbols])
        if self.bbox is not None:
            return f'<span class="ocrx_word" title="bbox {self.bbox[0]} {self.bbox[1]} {self.bbox[0] + self.bbox[2]} {self.bbox[1] + self.bbox[3]}; x_wconf {self.confidence}">{symbols}</span>'
        return self.text

    def get_confidence_html(self) -> str:
        symbols = "".join([symbol.get_confidence_html() for symbol in self.symbols])
        return f'<span style="background-color: {self.get_confidence_color()}">{symbols}</span>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "word",
            "text": self.text,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "word_font_attributes": self.word_font_attributes,
            "word_recognition_language": self.word_recognition_language,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultWord":
        instance = cls()
        instance.text = data.get("text", "")
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        instance.word_font_attributes = data.get("word_font_attributes", {})
        instance.word_recognition_language = data.get("word_recognition_language", "")
        instance.symbols = [
            OCRResultSymbol.from_dict(s) for s in data.get("symbols", [])
        ]
        return instance

    def __repr__(self) -> str:
        return f"OCRResultWord(bbox={self.bbox}, confidence={self.confidence}, symbols={self.symbols})"


class OCRResultSymbol(OCRResultElement):
    def __init__(self) -> None:
        self.text: str = ""

    def get_text(self) -> str:
        return self.text

    def get_hocr(self) -> str:
        if self.bbox is not None:
            return f'<span class="ocrx_symbol" title="bbox {self.bbox[0]} {self.bbox[1]} {self.bbox[0] + self.bbox[2]} {self.bbox[1] + self.bbox[3]}; x_wconf {self.confidence}">{self.text}</span>'
        return self.text

    def get_confidence_html(self) -> str:
        return f'<span style="background-color: {self.get_confidence_color()}">{self.text}</span>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "symbol",
            "text": self.text,
            "bbox": self.bbox,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultSymbol":
        instance = cls()
        instance.text = data.get("text", "")
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        return instance

    def __repr__(self) -> str:
        return f"OCRResultSymbol(bbox={self.bbox}, confidence={self.confidence})"
