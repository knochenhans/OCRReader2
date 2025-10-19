from typing import Callable, List, Optional

from iso639 import Lang
from SettingsManager import SettingsManager

from OCRReader2.page.ocr_box import OCRBox


class OCREngine:
    def __init__(self, settings: Optional[SettingsManager] = None) -> None:
        self.project_settings = settings

        self.langs_list: List[str] = []
        self.langs: str = ""

        if settings:
            self.langs_list = settings.settings.get("langs", [])
            self.langs = self.generate_lang_str(self.langs_list)

    def recognize_box_text(
        self,
        image_path: str,
        box: OCRBox,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        return ""

    def get_available_langs(self) -> List[Lang]:
        return []

    def generate_lang_str(self, langs: List[str]) -> str:
        lang_langs: List[Lang] = []
        for lang in langs:
            lang_langs.append(Lang(lang))

        return "+".join([lang.pt2t for lang in lang_langs])
