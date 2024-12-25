from typing import List, Optional

from page.ocr_box import OCRBox


class LayoutAnalyzer:
    def __init__(self, langs: Optional[List[str]]) -> None:
        self.langs = langs

    def analyze_layout(
        self,
        image_path: str,
        ppi: int,
        region: Optional[tuple[int, int, int, int]] = None,
        size_threshold: int = 0,
    ) -> List[OCRBox]:
        return []
