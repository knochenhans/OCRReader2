from typing import List, Optional

from loguru import logger
from tesserocr import PSM, PT, RIL, PyTessBaseAPI, iterate_level
from src.ocr_engine.layout_analyzer import LayoutAnalyzer
from src.ocr_engine.ocr_box import (
    HorizontalLine,
    ImageBox,
    OCRBox,
    TextBox,
    VerticalLine,
)
from src.ocr_engine.block_type import BoxType


class LayoutAnalyzerTesserOCR(LayoutAnalyzer):
    def __init__(self, langs: Optional[List[str]]) -> None:
        super().__init__(langs)
        self.api = PyTessBaseAPI()

    def analyze_layout(
        self,
        image_path: str,
        ppi: int,
        from_header: int = 0,
        to_footer: int = 0,
        size_threshold: int = 0,
    ) -> List[OCRBox]:
        logger.info("Analyzing layout for image: {}", image_path)
        blocks: List[OCRBox] = []

        if self.langs:
            from src.ocr_engine.ocr_engine_tesserocr import generate_lang_str
            lang_str = generate_lang_str(self.langs)
            self.api.Init(lang=lang_str, psm=PSM.AUTO_ONLY)
        else:
            self.api.Init(psm=PSM.AUTO_ONLY)

        self.api.SetImageFile(image_path)
        self.api.SetSourceResolution(ppi)
        self.api.SetPageSegMode(PSM.AUTO_ONLY)
        page_it = self.api.AnalyseLayout()

        if page_it:
            for result in iterate_level(page_it, RIL.BLOCK):
                left, top, right, bottom = result.BoundingBox(RIL.BLOCK)
                x, y, w, h = left, top + from_header, right - left, bottom - top

                if w * h < size_threshold:
                    logger.info(f"Skipping block with size {w}x{h}")
                    continue

                block_type = result.BlockType()
                type = BoxType.UNKNOWN

                match block_type:
                    case PT.FLOWING_TEXT | PT.PULLOUT_TEXT:
                        type = BoxType.FLOWING_TEXT
                        blocks.append(TextBox(x, y, w, h, ""))
                    case PT.HEADING_TEXT:
                        type = BoxType.HEADING_TEXT
                        blocks.append(TextBox(x, y, w, h, "", tag="h1"))
                    case PT.CAPTION_TEXT:
                        type = BoxType.CAPTION_TEXT
                        blocks.append(TextBox(x, y, w, h, "", tag="figcaption"))
                    case PT.FLOWING_IMAGE | PT.HEADING_IMAGE | PT.PULLOUT_IMAGE:
                        type = BoxType.FLOWING_IMAGE
                        blocks.append(ImageBox(x, y, w, h))
                    case PT.HORZ_LINE:
                        type = BoxType.HORZ_LINE
                        blocks.append(HorizontalLine(x, y, w, h))
                    case PT.VERT_LINE:
                        type = BoxType.VERT_LINE
                        blocks.append(VerticalLine(x, y, w, h))
                    case PT.EQUATION:
                        type = BoxType.EQUATION
                        blocks.append(OCRBox(x, y, w, h, type))
                    case PT.INLINE_EQUATION:
                        type = BoxType.INLINE_EQUATION
                        blocks.append(OCRBox(x, y, w, h, type))
                    case PT.TABLE:
                        type = BoxType.TABLE
                        blocks.append(OCRBox(x, y, w, h, type))
                    case PT.VERTICAL_TEXT:
                        type = BoxType.VERTICAL_TEXT
                        blocks.append(OCRBox(x, y, w, h, type))
                    case PT.NOISE:
                        type = BoxType.NOISE
                        blocks.append(OCRBox(x, y, w, h, type))
                    case PT.COUNT:
                        type = BoxType.COUNT
                        blocks.append(OCRBox(x, y, w, h, type))
                    case _:
                        type = BoxType.UNKNOWN
                        blocks.append(OCRBox(x, y, w, h, type))

                blocks[-1].class_ = type.value

        logger.info("Layout analysis result: {} blocks found", len(blocks))
        return blocks
