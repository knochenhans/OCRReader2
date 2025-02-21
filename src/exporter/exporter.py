from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from PIL import Image
import os

from ocr_engine.ocr_result import OCRResultBlock, OCRResultParagraph  # type: ignore
from page.box_type import BoxType  # type: ignore


class Exporter(ABC):
    def __init__(self, output_path: str, filename: str) -> None:
        self.output_path: str = output_path
        self.filename: str = filename
        self.project_export_data: Dict[str, Any] = {}
        self.images: Dict[str, Dict[str, str]] = {}
        self.scaling_factor: float = 1

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        self.project_export_data = project_export_data
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def export_page(self, page_export_data: Dict[str, Any]) -> None:
        pass

    def pixel_to_cm(self, pixels: int, ppi: int, rasterize: int = 2) -> float:
        return round(pixels / ppi * 2.54, rasterize)

    def save_cropped_image(
        self,
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
        image_name: str = "",
    ) -> str:
        image: Image.Image = Image.open(image_path)
        cropped_image: Image.Image = image.crop((x, y, x + width, y + height))
        cropped_image.save(output_path)

        if image_name == "":
            image_name = f"image_{len(self.images)}"

        image_info: Dict[str, str] = {
            "path": output_path,
            "name": image_name,
            "id": image_name,
        }

        self.images[image_name] = image_info
        return output_path

    def find_mean_font_size(
        self, ocr_result_paragraph: OCRResultParagraph, rasterize: int = 0
    ) -> float:
        total_font_size: float = 0
        total_words: int = 0
        for line in ocr_result_paragraph.lines:
            for word in line.words:
                total_font_size += word.word_font_attributes["pointsize"]
                total_words += 1
        return round(total_font_size / total_words, rasterize)

    def get_text(
        self,
        ocr_result_block: Optional[OCRResultBlock],
    ) -> str:
        text: str = ""
        if ocr_result_block:
            text = ocr_result_block.get_text()
        return text

    def get_page_content(self, export_data: Dict[str, Any]) -> str:
        content: str = ""
        for export_data_entry in export_data["boxes"]:
            if export_data_entry["type"] in [
                BoxType.FLOWING_TEXT,
                BoxType.HEADING_TEXT,
                BoxType.PULLOUT_TEXT,
                BoxType.VERTICAL_TEXT,
                BoxType.CAPTION_TEXT,
            ]:
                ocr_result_block: Optional[OCRResultBlock] = export_data_entry.get(
                    "ocr_results", None
                )
                if ocr_result_block:
                    content += self.get_text(ocr_result_block)
        return content
