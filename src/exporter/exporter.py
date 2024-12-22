from typing import Dict, Any
from abc import ABC, abstractmethod
from PIL import Image

from src.ocr_engine.ocr_result import OCRResultParagraph


class Exporter(ABC):
    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    @abstractmethod
    def export(self, export_data: Dict[str, Any]) -> None:
        pass

    def pixel_to_cm(self, pixels: int, ppi: int, rasterize: int = 2) -> float:
        return round(pixels / ppi * 2.54, rasterize)
    
    def save_cropped_image(
        self, image_path: str, x: int, y: int, width: int, height: int, output_path: str
    ) -> str:
        image = Image.open(image_path)
        cropped_image = image.crop((x, y, x + width, y + height))
        cropped_image.save(output_path)
        return output_path

    def find_mean_font_size(self, ocr_result_paragraph: OCRResultParagraph, rasterize: int = 0) -> float:
        total_font_size = 0
        total_words = 0
        for line in ocr_result_paragraph.lines:
            for word in line.words:
                total_font_size += word.word_font_attributes["pointsize"]
                total_words += 1
        return round(total_font_size / total_words, rasterize)