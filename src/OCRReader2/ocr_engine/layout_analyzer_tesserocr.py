from typing import Dict, List, Optional, Tuple, Type

from loguru import logger
from PIL import Image
from SettingsManager import SettingsManager
from tesserocr import PSM, PT, RIL, PyTessBaseAPI, iterate_level

from OCRReader2.ocr_engine.layout_analyzer import LayoutAnalyzer
from OCRReader2.page.box_type import BoxType
from OCRReader2.page.ocr_box import ImageBox, LineBox, OCRBox, TextBox


class LayoutAnalyzerTesserOCR(LayoutAnalyzer):
    def __init__(self, project_settings: Optional[SettingsManager] = None) -> None:
        super().__init__(project_settings)

        path = "./"

        if self.project_settings:
            path = self.project_settings.get("tesseract_data_path", path)

        lang = "eng"

        if self.langs:
            lang = self.langs

        self.api = PyTessBaseAPI(lang=lang, path=path)

    def analyze_layout(
        self,
        image_path: str,
        region: Optional[tuple[int, int, int, int]] = None,
    ) -> List[OCRBox]:
        logger.info(f"Analyzing layout in box ({region}) for image: {image_path}")
        blocks: List[OCRBox] = []

        lang = "eng"

        if self.langs:
            lang = self.langs

        self.api.Init(lang=lang, psm=PSM.AUTO_ONLY)

        self.set_variables()

        ppi = 300
        x_size_threshold = 0
        y_size_threshold = 0

        if self.project_settings:
            ppi = self.project_settings.get("ppi", ppi)
            x_size_threshold = self.project_settings.get(
                "x_size_threshold", x_size_threshold
            )
            y_size_threshold = self.project_settings.get(
                "y_size_threshold", y_size_threshold
            )

        self.api.SetImageFile(image_path)
        self.api.SetSourceResolution(ppi)
        self.api.SetPageSegMode(PSM.AUTO)

        # Use the whole image if no region is specified
        image = Image.open(image_path)
        width, height = image.size

        region = region or (0, 0, width, height)

        # Check if the region is valid
        if region[0] < 0 or region[1] < 0 or region[2] > width or region[3] > height:
            logger.error(
                f"Invalid region: {region} for image with size {width}x{height}"
            )
            return blocks

        # Ensure the region is not completely zero for all sizes
        if region[2] - region[0] == 0 or region[3] - region[1] == 0:
            logger.error(f"Region has zero width or height: {region}")
            return blocks

        self.api.SetRectangle(*region)

        page_it = self.api.AnalyseLayout()

        if page_it:
            block_number = 0
            for result in iterate_level(page_it, RIL.BLOCK):
                left, top, right, bottom = result.BoundingBox(RIL.BLOCK)
                x, y, w, h = left, top, right - left, bottom - top

                if w < x_size_threshold or h < y_size_threshold:
                    logger.info(f"Skipping block with size {w}x{h}")
                    continue

                box_type = result.BlockType()
                type = BoxType.UNKNOWN

                box_type_map: Dict[PT, Tuple[BoxType, Type[OCRBox]]] = {
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

        logger.info("Layout analysis result: {} blocks found", len(blocks))
        return self.CleanupBoxes(blocks)

    def set_variables(self):
        if self.project_settings:
            variables_string = self.project_settings.get("tesseract_options", "")

            if variables_string == "":
                return

            # Split string into x=y pairs
            variables_pairs = variables_string.split(";")

            for pair in variables_pairs:
                key, value = pair.split("=")
                self.api.SetVariable(key, value)

    def CleanupBoxes(self, boxes: List[OCRBox]) -> List[OCRBox]:
        image_boxes: List[ImageBox] = [box for box in boxes if isinstance(box, ImageBox)]
        text_boxes: List[TextBox] = [box for box in boxes if isinstance(box, TextBox)]

        # Remove all text boxes that are contained in or intersect with an image box
        for image_box in image_boxes:
            text_boxes = [
                text_box
                for text_box in text_boxes
                if not (image_box.contains(text_box) or image_box.intersects(text_box))
            ]

        # Merge all overlapping text boxes
        merged_text_boxes: List[TextBox] = []
        for text_box in text_boxes:
            if not merged_text_boxes:
                merged_text_boxes.append(text_box)
            else:
                last_box = merged_text_boxes[-1]
                if last_box.intersects(text_box):
                    last_box.x = min(last_box.x, text_box.x)
                    last_box.y = min(last_box.y, text_box.y)
                    last_box.width = (
                        max(last_box.x + last_box.width, text_box.x + text_box.width)
                        - last_box.x
                    )
                    last_box.height = (
                        max(last_box.y + last_box.height, text_box.y + text_box.height)
                        - last_box.y
                    )
                    last_box.confidence = max(last_box.confidence, text_box.confidence)

                else:
                    merged_text_boxes.append(text_box)

        return list(image_boxes + merged_text_boxes)
