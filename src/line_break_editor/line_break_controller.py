from spellchecker import SpellChecker

from page.ocr_box import TextBox # type: ignore


class LineBreakController:
    def __init__(self, ocr_text_box: TextBox, lang: str) -> None:
        self.ocr_box = ocr_text_box
        self.lang = lang

        self.spell = SpellChecker(language=self.lang)

    def get_text(self) -> str:
        text = ""

        if self.ocr_box.user_text:
            text = self.ocr_box.user_text
        else:
            if self.ocr_box.ocr_results:
                text = self.ocr_box.ocr_results.get_text()
        return text

    def set_text(self, text: str) -> None:
        self.ocr_box.user_text = text
