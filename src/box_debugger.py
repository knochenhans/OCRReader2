from typing import List

import cv2
from ocr_engine.ocr_result import OCRResultBlock
from page.ocr_box import OCRBox
from page.box_type import BoxType


class BoxDebugger:
    def __init__(self) -> None:
        self.color_map = {
            BoxType.UNKNOWN: (0, 255, 0),  # BGR -> Green
            BoxType.FLOWING_TEXT: (0, 0, 255),  # BGR -> Red
            BoxType.HEADING_TEXT: (255, 0, 255),  # BGR -> Magenta
            BoxType.PULLOUT_TEXT: (255, 255, 0),  # BGR -> Cyan
            BoxType.EQUATION: (0, 255, 255),  # BGR -> Yellow
            BoxType.INLINE_EQUATION: (255, 0, 0),  # BGR -> Blue
            BoxType.TABLE: (0, 128, 255),  # BGR -> Orange
            BoxType.VERTICAL_TEXT: (128, 128, 0),  # BGR -> Olive
            BoxType.CAPTION_TEXT: (128, 128, 128),  # BGR -> Gray
            BoxType.FLOWING_IMAGE: (255, 0, 0),  # BGR -> Blue
            BoxType.HEADING_IMAGE: (0, 128, 128),  # BGR -> Teal
            BoxType.PULLOUT_IMAGE: (128, 0, 0),  # BGR -> Maroon
            BoxType.HORZ_LINE: (64, 64, 64),  # BGR -> Dark Gray
            BoxType.VERT_LINE: (64, 64, 64),  # BGR -> Dark Gray
            BoxType.NOISE: (192, 192, 192),  # BGR -> Silver
            BoxType.COUNT: (255, 255, 255),  # BGR -> White
        }

    def _draw_boxes(
        self, image, boxes: List[OCRBox], confidence_threshold: float = 0.0
    ) -> None:
        def draw_text(image, text, position, color):
            cv2.putText(
                image,
                text,
                position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        previous_box = None
        for box in boxes:
            if box.confidence < confidence_threshold:
                continue
            x, y, w, h = box.x, box.y, box.width, box.height
            color = self.color_map.get(box.type, self.color_map[BoxType.UNKNOWN])

            # Add a light background tone
            overlay = image.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)

            alpha = 0.3  # Transparency factor
            cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

            # Draw the rectangle border
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

            # Display a symbol in the center of the rectangle if the block contains OCR results
            if box.ocr_results:
                # Display a symbol in the left upper corner of the rectangle if the block contains OCR results
                draw_text(image, "OK", (x + 5, y + 15), color)

                # Display the confidence below the rectangle
                draw_text(image, f"{box.confidence:.2f}", (x + 5, y + h + 20), color)

                if isinstance(box.ocr_results, OCRResultBlock):
                    for paragraph in box.ocr_results.paragraphs:
                        for line in paragraph.lines:

                            # Display the baseline
                            if line.baseline is not None:
                                cv2.line(
                                    image, line.baseline[0], line.baseline[1], color, 1
                                )

            # Display the box order in the right upper corner of the rectangle
            draw_text(image, str(box.order), (x + w + 5, y + 15), color)

            # Display the box type name at the top of the rectangle
            draw_text(image, box.type.name, (x + 5, y - 5), color)

            # Draw arrows between successive text boxes
            if (
                previous_box
                and previous_box.type
                in [
                    BoxType.FLOWING_TEXT,
                    BoxType.HEADING_TEXT,
                    BoxType.PULLOUT_TEXT,
                    BoxType.CAPTION_TEXT,
                    BoxType.VERTICAL_TEXT,
                ]
                and box.type
                in [
                    BoxType.FLOWING_TEXT,
                    BoxType.HEADING_TEXT,
                    BoxType.PULLOUT_TEXT,
                    BoxType.CAPTION_TEXT,
                    BoxType.VERTICAL_TEXT,
                ]
            ):
                prev_x, prev_y, prev_w, prev_h = (
                    previous_box.x,
                    previous_box.y,
                    previous_box.width,
                    previous_box.height,
                )
                start_point = (prev_x + prev_w // 2, prev_y + prev_h // 2)
                end_point = (x + w // 2, y + h // 2)

                # Create an overlay for the arrow
                overlay = image.copy()
                cv2.arrowedLine(
                    overlay, start_point, end_point, (0, 0, 255), 2, tipLength=0.05
                )
                alpha = 0.3  # Transparency factor
                cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

            previous_box = box

    def show_box(
        self, image_path: str, box: OCRBox, confidence_threshold: float = 0.0
    ) -> None:
        self.show_boxes(image_path, [box], confidence_threshold)

    def show_boxes(
        self, image_path: str, boxes: List[OCRBox], confidence_threshold: float = 0.0
    ) -> None:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Draw the rectangles on the image
        self._draw_boxes(image, boxes, confidence_threshold)

        # Display the image with the boxes
        cv2.imshow("Boxes", image)
        while True:
            if cv2.waitKey(1) == 27:  # Exit on ESC key
                break
        cv2.destroyAllWindows()
