from typing import List, Optional

from src.page.ocr_box import OCRBox


class LayoutAnalyzer:
    def __init__(self, langs: Optional[List[str]]) -> None:
        self.langs = langs

    def analyze_layout(
        self,
        image_path: str,
        ppi: int,
        from_header: int = 0,
        to_footer: int = 0,
        size_threshold: int = 0,
    ) -> List[OCRBox]:
        return []
