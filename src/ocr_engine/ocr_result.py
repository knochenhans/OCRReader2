from typing import List, Dict, Any, Optional, Tuple

from tesserocr import Justification

# Define a specific type for the bounding box
BoundingBox = Tuple[int, int, int, int]  # (x, y, width, height)


class OCRResultBlock:
    def __init__(self) -> None:
        self.bbox: Optional[BoundingBox] = None
        self.confidence: float = 0.0
        self.paragraphs: List[OCRResultParagraph] = []
        self.language: str = ""

    def add_paragraph(self, paragraph: "OCRResultParagraph") -> None:
        self.paragraphs.append(paragraph)

    def get_text(self) -> str:
        return "\n".join([paragraph.get_text() for paragraph in self.paragraphs])

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


class OCRResultParagraph:
    def __init__(self) -> None:
        self.bbox: Optional[BoundingBox] = None
        self.confidence: float = 0.0
        self.first_line_indent: bool = False
        self.is_crown: bool = False
        self.is_list_item: bool = False
        self.justification: Optional[Justification] = None
        self.lines: List[OCRResultLine] = []

    def add_line(self, line: "OCRResultLine") -> None:
        self.lines.append(line)

    def get_text(self) -> str:
        return " ".join([line.get_text() for line in self.lines])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paragraph",
            "bbox": self.bbox,
            "confidence": self.confidence,
            "lines": [line.to_dict() for line in self.lines],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OCRResultParagraph":
        instance = cls()
        bbox = data.get("bbox", None)
        if bbox is not None:
            instance.bbox = tuple(bbox)
        instance.confidence = data.get("confidence", 0.0)
        instance.lines = [OCRResultLine.from_dict(l) for l in data.get("lines", [])]
        return instance

    def __repr__(self) -> str:
        return f"OCRResultParagraph(lines={self.lines})"


class OCRResultLine:
    def __init__(self) -> None:
        self.bbox: Optional[BoundingBox] = None
        self.confidence: float = 0.0
        self.baseline: Optional[tuple[tuple[int, int], tuple[int, int]]] = None
        self.words: List[OCRResultWord] = []

    def add_word(self, word: "OCRResultWord") -> None:
        self.words.append(word)

    def get_text(self) -> str:
        return " ".join([word.text for word in self.words])

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


class OCRResultWord:
    def __init__(self) -> None:
        self.text: str = ""
        self.bbox: Optional[BoundingBox] = None
        self.confidence: float = 0.0
        self.word_font_attributes: Dict[str, Any] = {}
        self.word_recognition_language: str = ""

        # TODO:
        # def SymbolIsSuperscript(self) -> bool:
        # def SymbolIsSubscript(self) -> bool:
        # def SymbolIsDropcap(self) -> bool:

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "word",
            "text": self.text,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "word_font_attributes": self.word_font_attributes,
            "word_recognition_language": self.word_recognition_language,
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
        return instance

    def __repr__(self) -> str:
        return f"OCRResultWord(bbox={self.bbox}, confidence={self.confidence})"
