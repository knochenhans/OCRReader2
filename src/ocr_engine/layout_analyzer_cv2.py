from typing import List, Optional, Tuple

import cv2
import numpy as np
from loguru import logger

from ocr_engine.layout_analyzer import LayoutAnalyzer  # type: ignore
from page.box_type import BoxType  # type: ignore
from page.ocr_box import OCRBox, TextBox  # type: ignore
from settings.settings import Settings  # type: ignore


class LayoutAnalyzerCV2(LayoutAnalyzer):
    def __init__(self, settings: Optional[Settings] = None) -> None:
        super().__init__(settings)

    def analyze_layout(
        self,
        image_path: str,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> List[OCRBox]:
        ocr_boxes: List[OCRBox] = []

        # Load the image
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to create a binary image
        _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        # Apply dilation to enhance regions
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=5)

        # Find contours
        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Process each contour
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # If a region is specified, filter contours outside the region
            if region:
                rx, ry, rw, rh = region
                if not (rx <= x <= rx + rw and ry <= y <= ry + rh):
                    continue

            # Determine the box type (for simplicity, assume all are text boxes)
            box_type = BoxType.FLOWING_TEXT
            box_class = TextBox

            # Create a box instance
            box = box_class(
                x=x,
                y=y,
                width=w,
                height=h,
                type=box_type,
            )
            ocr_boxes.append(box)

            logger.debug(
                f"Detected box at ({x}, {y}) with size {w}x{h} and type {box_type.name}"
            )

        ocr_boxes.sort(key=lambda box: (box.y, box.x))

        logger.info(f"Layout analysis completed: {len(ocr_boxes)} boxes detected.")
        return ocr_boxes
