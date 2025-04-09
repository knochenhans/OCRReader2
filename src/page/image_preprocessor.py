import os
from typing import Tuple

import cv2


class ImagePreprocessor:
    def __init__(self, image_path: str) -> None:
        self.image_path: str = image_path
        self.image = cv2.imread(image_path)

        # Check if the image was successfully loaded
        if self.image is None:
            raise ValueError("Error: Unable to load image. Please check path.")

    def erase_boxes(
        self, boxes: list[Tuple[int, int, int, int]], output_dir: str
    ) -> str:
        # Create a copy of the image to modify
        modified_image = self.image.copy()

        # Fill each specified area with white
        for box_coordinates in boxes:
            x, y, w, h = box_coordinates
            modified_image[y : y + h, x : x + w] = (
                255,
                255,
                255,
            )  # Set the region to white

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate the output filename
        output_filename = os.path.join(output_dir, "preprocessed_image.jpg")

        # Save the modified image without displaying it
        cv2.imwrite(output_filename, modified_image)

        return output_filename
