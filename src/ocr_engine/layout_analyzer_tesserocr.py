from typing import List, Optional

from loguru import logger
from tesserocr import PSM, PT, RIL, PyTessBaseAPI, iterate_level # type: ignore
from ocr_engine.layout_analyzer import LayoutAnalyzer # type: ignore
from page.ocr_box import ( # type: ignore
    LineBox,
    ImageBox,
    OCRBox,
    TextBox,
)
from page.box_type import BoxType # type: ignore
from PIL import Image


class LayoutAnalyzerTesserOCR(LayoutAnalyzer):
    def __init__(self, langs: Optional[List[str]]) -> None:
        super().__init__(langs)
        self.api = PyTessBaseAPI()

    def analyze_layout(
        self,
        image_path: str,
        ppi: int,
        region: Optional[tuple[int, int, int, int]] = None,
        size_threshold: int = 0,
    ) -> List[OCRBox]:
        logger.info(f"Analyzing layout in box ({region}) for image: {image_path}")
        blocks: List[OCRBox] = []

        if self.langs:
            from ocr_engine.ocr_engine_tesserocr import generate_lang_str # type: ignore

            lang_str = generate_lang_str(self.langs)
            self.api.Init(lang=lang_str, psm=PSM.AUTO_ONLY)
        else:
            self.api.Init(psm=PSM.AUTO_ONLY)

        self.api.SetImageFile(image_path)
        self.api.SetSourceResolution(ppi)
        self.api.SetPageSegMode(PSM.AUTO_ONLY)

        # Use the whole image if no region is specified
        image = Image.open(image_path)
        width, height = image.size

        region = region or (0, 0, width, height)

        self.api.SetRectangle(*region)

        page_it = self.api.AnalyseLayout()

        if page_it:
            block_number = 0
            for result in iterate_level(page_it, RIL.BLOCK):
                left, top, right, bottom = result.BoundingBox(RIL.BLOCK)
                x, y, w, h = left, top, right - left, bottom - top

                if w * h < size_threshold:
                    logger.info(f"Skipping block with size {w}x{h}")
                    continue

                box_type = result.BlockType()
                type = BoxType.UNKNOWN

                box_type_map = {
                    PT.FLOWING_TEXT: (BoxType.FLOWING_TEXT, TextBox),
                    PT.PULLOUT_TEXT: (BoxType.PULLOUT_TEXT, TextBox),
                    PT.HEADING_TEXT: (BoxType.HEADING_TEXT, TextBox),
                    PT.CAPTION_TEXT: (BoxType.CAPTION_TEXT, TextBox),
                    PT.FLOWING_IMAGE: (BoxType.FLOWING_IMAGE, ImageBox),
                    PT.HEADING_IMAGE: (BoxType.HEADING_IMAGE, ImageBox),
                    PT.PULLOUT_IMAGE: (BoxType.PULLOUT_IMAGE, ImageBox),
                    PT.HORZ_LINE: (BoxType.HORZ_LINE, LineBox),
                    PT.VERT_LINE: (BoxType.VERT_LINE, LineBox),
                    PT.EQUATION: (BoxType.EQUATION, OCRBox),
                    PT.INLINE_EQUATION: (BoxType.INLINE_EQUATION, OCRBox),
                    PT.TABLE: (BoxType.TABLE, OCRBox),
                    PT.VERTICAL_TEXT: (BoxType.VERTICAL_TEXT, OCRBox),
                    PT.NOISE: (BoxType.NOISE, OCRBox),
                    PT.COUNT: (BoxType.COUNT, OCRBox),
                }

                type, box_class = box_type_map.get(box_type, (BoxType.UNKNOWN, OCRBox))
                blocks.append(box_class(x, y, w, h, type))

                logger.debug(
                    f"Block #{block_number} at ({x}, {y}) with size {w}x{h} and type {box_type} ({type.name}) found"
                )
                block_number += 1

                blocks[-1].class_ = type.value

        logger.info("Layout analysis result: {} blocks found", len(blocks))
        return blocks
