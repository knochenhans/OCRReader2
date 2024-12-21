from typing import Dict, Any
from abc import ABC, abstractmethod
from PIL import Image


class Exporter(ABC):
    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    @abstractmethod
    def export(self, export_data: Dict[str, Any]) -> None:
        pass

    def pixel_to_cm(self, pixels: int, ppi: int) -> float:
        return pixels / ppi * 2.54

    def save_cropped_image(
        self, image_path: str, x: int, y: int, width: int, height: int, output_path: str
    ) -> str:
        image = Image.open(image_path)
        cropped_image = image.crop((x, y, x + width, y + height))
        cropped_image.save(output_path)
        return output_path
