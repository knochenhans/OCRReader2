import concurrent.futures
import queue

from tesserocr import PyTessBaseAPI, RIL, PSM, iterate_level
from PIL import Image
from typing import Callable, List, Dict, Optional, Union
from iso639 import Lang  # type: ignore
from loguru import logger
from src.page.layout_analyzer_tesserocr import LayoutAnalyzerTesserOCR
from src.page.ocr_box import OCRBox
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultLine,
    OCRResultParagraph,
    OCRResultWord,
)
from src.page.ocr_box import (
    OCRBox,
    TextBox
)
from src.ocr_engine.ocr_engine import OCREngine

NUM_THREADS = 4
tesserocr_queue = queue.Queue()


def generate_lang_str(langs: List) -> str:
    lang_langs = []
    for lang in langs:
        lang_langs.append(Lang(lang))

    return "+".join([lang.pt2t for lang in lang_langs])


def extract_text_from_iterator(ri) -> List[OCRResultBlock]:
    blocks = []
    current_block = None
    current_paragraph = None
    current_line = None

    for result_word in iterate_level(ri, RIL.WORD):
        if result_word.IsAtBeginningOf(RIL.BLOCK):
            current_block = OCRResultBlock()
            current_block.text = ri.GetUTF8Text(RIL.BLOCK).strip()
            current_block.bbox = result_word.BoundingBox(RIL.BLOCK)
            current_block.confidence = result_word.Confidence(RIL.BLOCK)
            blocks.append(current_block)

        if result_word.IsAtBeginningOf(RIL.PARA):
            current_paragraph = OCRResultParagraph()
            current_paragraph.text = ri.GetUTF8Text(RIL.PARA).strip()
            current_paragraph.bbox = result_word.BoundingBox(RIL.PARA)
            current_paragraph.confidence = result_word.Confidence(RIL.PARA)
            if current_block is not None:
                current_block.add_paragraph(current_paragraph)

        if result_word.IsAtBeginningOf(RIL.TEXTLINE):
            current_line = OCRResultLine()
            current_line.text = ri.GetUTF8Text(RIL.TEXTLINE).strip()
            current_line.bbox = result_word.BoundingBox(RIL.TEXTLINE)
            current_line.confidence = result_word.Confidence(RIL.TEXTLINE)
            current_line.baseline = result_word.Baseline(RIL.TEXTLINE)
            if current_paragraph is not None:
                current_paragraph.add_line(current_line)

        if not result_word.Empty(RIL.WORD):
            current_word = OCRResultWord()
            current_word.text = result_word.GetUTF8Text(RIL.WORD).strip()
            current_word.bbox = result_word.BoundingBox(RIL.WORD)
            current_word.confidence = result_word.Confidence(RIL.WORD)
            current_word.word_font_attributes = result_word.WordFontAttributes()
            current_word.word_recognition_language = (
                result_word.WordRecognitionLanguage()
            )
            if current_line is not None:
                current_line.add_word(current_word)

    logger.info(f"Extracted text from iterator: {len(blocks)} blocks found")
    return blocks


def perform_ocr(api: PyTessBaseAPI, box: OCRBox) -> OCRBox:
    try:
        if isinstance(box, TextBox):
            # TODO: Find a better way to handle padding/expanding
            box.expand(10)
            api.SetRectangle(box.x, box.y, box.width, box.height)
            if api.Recognize():
                results = extract_text_from_iterator(api.GetIterator())

                if len(results) == 1:
                    if isinstance(results[0], OCRResultBlock):
                        box.text = results[0].text
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
    def __init__(self, langs: Optional[List]) -> None:
        super().__init__(langs)
        for _ in range(NUM_THREADS):
            api = PyTessBaseAPI()
            lang_str = generate_lang_str(self.langs) if self.langs else None
            if lang_str:
                api.Init(lang=lang_str)
            else:
                api.Init()
            tesserocr_queue.put(api)

        self.results: List[OCRBox] = []
        logger.info(f"OCREngineTesserOCR initialized with languages: {langs}")

    def detect_orientation_script(
        self, image_path: str, ppi: int
    ) -> Dict[str, Union[int, str]]:
        logger.info(f"Detecting orientation and script for image: {image_path}")
        api = tesserocr_queue.get()
        try:
            if self.langs:
                lang_str = generate_lang_str(self.langs)
                api.Init(lang=lang_str, psm=PSM.OSD_ONLY)
            else:
                api.Init(psm=PSM.OSD_ONLY)

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

    def analyze_layout(
        self,
        image_path: str,
        ppi: int,
        size_threshold: int = 0,
        region: Optional[tuple[int, int, int, int]] = None,
    ) -> List[OCRBox]:
        layout_analyzer = LayoutAnalyzerTesserOCR(self.langs)
        return layout_analyzer.analyze_layout(image_path, ppi, region, size_threshold)

    def recognize(
        self, image_path: str, ppi: int, box: Optional[OCRBox] = None
    ) -> List[OCRResultBlock]:
        logger.info(f"Recognizing text for image: {image_path}")
        api = tesserocr_queue.get()
        try:
            if self.langs:
                lang_str = generate_lang_str(self.langs)
                api.Init(lang=lang_str)
            api.SetImageFile(image_path)
            api.SetSourceResolution(ppi)

            if box:
                box.expand(self.settings["padding"])
                api.SetRectangle(box.x, box.y, box.width, box.height)
                logger.info(f"Recognizing text within box: {box}")

            api.Recognize()
            ri = api.GetIterator()
            result = extract_text_from_iterator(ri)
            logger.info(f"Text recognition result: {len(result)} blocks found")
            return result
        finally:
            tesserocr_queue.put(api)

    def recognize_box_text(self, image_path: str, ppi: int, box: OCRBox) -> str:
        logger.info(f"Recognizing text for box in image: {image_path}")
        api = tesserocr_queue.get()
        if self.langs:
            lang_str = generate_lang_str(self.langs)
            api.Init(lang=lang_str)
        return recognize_text(api, box, image_path, ppi)

    def recognize_boxes(self, image_path: str, ppi: int, boxes: List[OCRBox]) -> None:
        logger.info(f"Recognizing text for multiple boxes in image: {image_path}")
        self.results: List[OCRBox] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [
                executor.submit(self._perform_ocr_with_queue, image_path, ppi, box)
                for box in boxes
            ]
            for future in concurrent.futures.as_completed(futures):
                box = future.result()
                if isinstance(box, TextBox) and box.text:
                    self.results.append(box)

    def _perform_ocr_with_queue(self, image_path: str, ppi: int, box: OCRBox) -> OCRBox:
        api = tesserocr_queue.get()
        try:
            if self.langs:
                lang_str = generate_lang_str(self.langs)
                api.Init(lang=lang_str)
            api.SetImageFile(image_path)
            api.SetSourceResolution(ppi)
            return perform_ocr(api, box)
        finally:
            tesserocr_queue.put(api)

    def handle_result(self, box: OCRBox) -> None:
        logger.info(f"Handling result for box: {box}")
        self.results.append(box)
        logger.info(f"Results: {self.results}")


def recognize_text(
    api, box: OCRBox, image_path: Optional[str] = None, ppi: Optional[int] = None
) -> str:
    try:
        if image_path:
            api.SetImageFile(image_path)
        if ppi:
            api.SetSourceResolution(ppi)
        box.expand(10)
        api.SetRectangle(box.x, box.y, box.width, box.height)
        text = api.GetUTF8Text().strip()
        if isinstance(box, TextBox):
            box.text = text
            box.confidence = api.MeanTextConf()
        logger.info(f"Recognized text: {text}")
        return text
    except Exception as e:
        logger.error(f"Error recognizing text: {e}")
        return ""
    finally:
        tesserocr_queue.put(api)
