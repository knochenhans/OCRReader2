class OCRResultBlock:
    def __init__(self):
        self.text = ""
        self.bbox = None  # Bounding Box
        self.confidence = 0.0
        self.paragraphs = []
        self.language = ""

    def add_paragraph(self, paragraph):
        self.paragraphs.append(paragraph)

    def __repr__(self) -> str:
        return f"OCRResultBlock(text={self.text}, paragraphs={self.paragraphs}, bbox={self.bbox}, confidence={self.confidence}, language={self.language})"


class OCRResultParagraph:
    def __init__(self):
        self.text = ""
        self.bbox = None
        self.confidence = 0.0
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def __repr__(self) -> str:
        return f"OCRResultParagraph(text={self.text}, lines={self.lines})"


class OCRResultLine:
    def __init__(self):
        self.text = ""
        self.bbox = None
        self.confidence = 0.0
        self.words = []

    def add_word(self, word):
        self.words.append(word)

    def __repr__(self) -> str:
        return f"OCRResultLine(text={self.text}, words={self.words})"


class OCRResultWord:
    def __init__(self):
        self.text = ""
        self.bbox = None
        self.confidence = 0.0

    def __repr__(self) -> str:
        return f"OCRResultWord(text={self.text}, bbox={self.bbox}, confidence={self.confidence})"
