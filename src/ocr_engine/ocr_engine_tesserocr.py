import concurrent.futures
import queue
from typing import Dict, List, Optional, Union

from iso639 import Lang  # type: ignore
from loguru import logger
from tesserocr import PSM, RIL, PyTessBaseAPI, iterate_level  # type: ignore

from ocr_engine.ocr_engine import OCREngine  # type: ignore
from ocr_engine.ocr_result import (  # type: ignore
    OCRResultBlock,
    OCRResultLine,
    OCRResultParagraph,
    OCRResultSymbol,
    OCRResultWord,
)
from page.ocr_box import OCRBox, TextBox  # type: ignore
from settings.settings import Settings  # type: ignore

NUM_THREADS = 4
tesserocr_queue: queue.Queue[PyTessBaseAPI] = queue.Queue()


def parse_ocr_results(ri) -> List[OCRResultBlock]:
    blocks = []
    current_block = None
    current_paragraph = None
    current_line = None
    current_word = None

    for result_symbol in iterate_level(ri, RIL.SYMBOL):
        if result_symbol.IsAtBeginningOf(RIL.BLOCK):
            current_block = OCRResultBlock()
            current_block.bbox = result_symbol.BoundingBox(RIL.BLOCK)
            current_block.confidence = result_symbol.Confidence(RIL.BLOCK)
            blocks.append(current_block)

        if result_symbol.IsAtBeginningOf(RIL.PARA):
            current_paragraph = OCRResultParagraph()
            current_paragraph.bbox = result_symbol.BoundingBox(RIL.PARA)
            current_paragraph.confidence = result_symbol.Confidence(RIL.PARA)

            justification, is_list_item, is_crown, first_line_indent = (
                ri.ParagraphInfo()
            )
            current_paragraph.justification = justification
            current_paragraph.is_list_item = is_list_item
            current_paragraph.is_crown = is_crown
            current_paragraph.first_line_indent = first_line_indent

            if current_block is not None:
                current_block.add_paragraph(current_paragraph)

        if result_symbol.IsAtBeginningOf(RIL.TEXTLINE):
            current_line = OCRResultLine()
            current_line.bbox = result_symbol.BoundingBox(RIL.TEXTLINE)
            current_line.confidence = result_symbol.Confidence(RIL.TEXTLINE)
            current_line.baseline = result_symbol.Baseline(RIL.TEXTLINE)
            if current_paragraph is not None:
                current_paragraph.add_line(current_line)

        if result_symbol.IsAtBeginningOf(RIL.WORD):
            current_word = OCRResultWord()
            current_word.bbox = result_symbol.BoundingBox(RIL.WORD)
            current_word.confidence = result_symbol.Confidence(RIL.WORD)
            current_word.word_font_attributes = result_symbol.WordFontAttributes()
            current_word.word_recognition_language = (
                result_symbol.WordRecognitionLanguage()
            )
            if current_line is not None:
                current_line.add_word(current_word)

        if not result_symbol.Empty(RIL.SYMBOL):
            current_symbol = OCRResultSymbol()
            current_symbol.text = result_symbol.GetUTF8Text(RIL.SYMBOL)
            current_symbol.bbox = result_symbol.BoundingBox(RIL.SYMBOL)
            current_symbol.confidence = result_symbol.Confidence(RIL.SYMBOL)
            if current_word is not None:
                current_word.add_symbol(current_symbol)

    logger.info(f"Extracted text from iterator: {len(blocks)} blocks found")
    return blocks


def perform_ocr(
    api: PyTessBaseAPI, box: OCRBox, settings: Optional[Settings] = None
) -> OCRBox:
    try:
        if isinstance(box, TextBox):
            padding = 10

            if settings:
                padding = settings.get("padding", padding)

            box.expand(padding)
            api.SetRectangle(box.x, box.y, box.width, box.height)
            api.SetPageSegMode(PSM.SINGLE_BLOCK)
            if api.Recognize():
                results = parse_ocr_results(api.GetIterator())

                if len(results) == 1:
                    if isinstance(results[0], OCRResultBlock):
                        box.confidence = results[0].confidence
                        box.ocr_results = results[0]
                        # logger.info("Recognized text for box: {}", box.text)
                elif len(results) > 1:
                    # TODO: Handle multiple blocks
                    logger.warning("More than one block found in box")

            box.shrink(10)
    except Exception as e:
        logger.error(f"Error in worker: {e}")
    return box


class OCREngineTesserOCR(OCREngine):
    def __init__(self, project_settings: Optional[Settings] = None) -> None:
        super().__init__(project_settings)

        self.path = "./"

        if self.project_settings:
            self.path = self.project_settings.get("tesseract_data_path", None)

        lang = "eng"

        if self.langs:
            lang = self.langs

        for _ in range(NUM_THREADS):
            api = PyTessBaseAPI(lang=lang, path=self.path)  # type: ignore
            self.set_variables(api)
            # api.Init(lang=lang, path=self.path)

            tesserocr_queue.put(api)

        self.results: List[OCRBox] = []
        logger.info(
            f"OCREngineTesserOCR initialized with languages: {self.langs}, path: {self.path}"
        )

    def detect_orientation_script(self, image_path: str) -> Dict[str, Union[int, str]]:
        logger.info(f"Detecting orientation and script for image: {image_path}")
        api = tesserocr_queue.get()

        lang = "eng"

        if self.langs:
            lang = self.langs

        try:
            api.Init(lang=lang, psm=PSM.OSD_ONLY, path=self.path)

            logger.info(
                f"Tesseract API initialized with language: {lang}, path: {self.path}, psm: {PSM.OSD_ONLY}"
            )

            ppi = 300

            if self.project_settings:
                ppi = self.project_settings.get("ppi", ppi)

            api.SetImageFile(image_path)
            api.SetSourceResolution(ppi)
            os = api.DetectOS()
            logger.info(f"Orientation and script detection result: {os}")
            return {
                "orientation": os["orientation"],
                "orientation_confidence": os["oconfidence"],
                "script": os["script"],
                "script_confidence": os["sconfidence"],
            }
        finally:
            tesserocr_queue.put(api)

    def recognize_box(self, image_path: str, boxes: List[OCRBox]) -> None:
        logger.info(f"Recognizing text for image: {image_path}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [
                executor.submit(self._perform_ocr_with_queue, image_path, box)
                for box in boxes
            ]
            for future in concurrent.futures.as_completed(futures):
                box = future.result()
                if isinstance(box, TextBox):
                    self.results.append(box)

    def recognize_box_text(self, image_path: str, box: OCRBox) -> str:
        logger.info(f"Recognizing text for box in image: {image_path}")
        api = tesserocr_queue.get()

        lang = "eng"

        if self.langs:
            lang = self.langs

        api.Init(lang=lang, psm=PSM.SINGLE_BLOCK, path=self.path)
        return self.recognize_text(api, box, image_path)

    def recognize_boxes(self, image_path: str, boxes: List[OCRBox]) -> None:
        logger.info(f"Recognizing text for multiple boxes in image: {image_path}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [
                executor.submit(self._perform_ocr_with_queue, image_path, box)
                for box in boxes
            ]
            for future in concurrent.futures.as_completed(futures):
                box = future.result()
                if isinstance(box, TextBox):
                    self.results.append(box)

    def _perform_ocr_with_queue(self, image_path: str, box: OCRBox) -> OCRBox:
        api = tesserocr_queue.get()

        lang = "eng"

        if self.langs:
            lang = self.langs

        try:
            api.Init(lang=lang, psm=PSM.SINGLE_BLOCK, path=self.path)

            logger.info(
                f"Tesseract API initialized with language: {lang}, path: {self.path}, psm: {PSM.SINGLE_BLOCK}"
            )

            ppi = 300

            if self.project_settings:
                ppi = self.project_settings.get("ppi", ppi)

            api.SetImageFile(image_path)
            api.SetSourceResolution(ppi)
            return perform_ocr(api, box, self.project_settings)
        except Exception as e:
            logger.error(f"Error in worker: {e}")
            return box
        finally:
            tesserocr_queue.put(api)

    def handle_result(self, box: OCRBox) -> None:
        logger.info(f"Handling result for box: {box}")
        self.results.append(box)
        logger.info(f"Results: {self.results}")

    def recognize_text(
        self,
        api,
        box: OCRBox,
        image_path: Optional[str] = None,
    ) -> str:
        try:
            if image_path:
                api.SetImageFile(image_path)

            ppi = 300

            if self.project_settings:
                ppi = self.project_settings.get("ppi", ppi)

            api.SetSourceResolution(ppi)
            box.expand(10)
            api.SetRectangle(box.x, box.y, box.width, box.height)
            text = api.GetUTF8Text().strip()
            if isinstance(box, TextBox):
                box.confidence = api.MeanTextConf()
            logger.info(f"Recognized text: {text}")
            return text
        except Exception as e:
            logger.error(f"Error recognizing text: {e}")
            return ""
        finally:
            tesserocr_queue.put(api)

    def get_available_langs(self) -> List[Lang]:
        api = tesserocr_queue.get()
        # try:
        langs = api.GetAvailableLanguages()

        if "osd" in langs:
            langs.remove("osd")

        return [Lang(lang) for lang in langs]
        # finally:
        #     tesserocr_queue.put(api)

    def set_variables(self, api: PyTessBaseAPI) -> None:
        if self.project_settings:
            variables_string = self.project_settings.get("tesseract_options", "")

            if variables_string == "":
                return

            # Split string into x=y pairs
            variables_pairs = variables_string.split(";")

            for pair in variables_pairs:
                key, value = pair.split("=")
                api.SetVariable(key, value)
