from typing import List, Optional

from iso639 import Lang
from page.ocr_box import OCRBox  # type: ignore
from settings import Settings  # type: ignore


class LayoutAnalyzer:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings

        self.langs_list: List[str] = []
        self.langs: str = ""

        if settings:
            self.langs_list = settings.settings.get("langs", [])
            self.langs = self.generate_lang_str(self.langs_list)

    def analyze_layout(
        self,
        image_path: str,
        region: Optional[tuple[int, int, int, int]] = None,
    ) -> List[OCRBox]:
        return []

    def generate_lang_str(self, langs: List[str]) -> str:
        lang_langs = []
        for lang in langs:
            lang_langs.append(Lang(lang))

        return "+".join([lang.pt2t for lang in lang_langs])
