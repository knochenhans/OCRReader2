from typing import Dict, Any
from abc import ABC, abstractmethod
from PIL import Image

from src.ocr_engine.ocr_result import OCRResultBlock, OCRResultParagraph
from src.page.ocr_box import BoxType


class Exporter(ABC):
    def __init__(self, output_path: str, filename: str) -> None:
        self.output_path = output_path
        self.filename = filename

        self.images = {}

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        self.project_export_data = project_export_data

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
        image = Image.open(image_path)
        cropped_image = image.crop((x, y, x + width, y + height))
        cropped_image.save(output_path)

        if image_name == "":
            image_name = f"image_{len(self.images)}"

        image = {
            "path": output_path,
            "name": image_name,
            "id": image_name,
        }

        self.images[image_name] = image
        return output_path

    def find_mean_font_size(
        self, ocr_result_paragraph: OCRResultParagraph, rasterize: int = 0
    ) -> float:
        total_font_size = 0
        total_words = 0
        for line in ocr_result_paragraph.lines:
            for word in line.words:
                total_font_size += word.word_font_attributes["pointsize"]
                total_words += 1
        return round(total_font_size / total_words, rasterize)

    def get_text(
        self,
        ocr_result_block: OCRResultBlock,
    ) -> str:
        if ocr_result_block:
            for ocr_result_paragraph in ocr_result_block.paragraphs:
                text = "\n".join(
                    [
                        " ".join([word.text for word in line.words])
                        for line in ocr_result_paragraph.lines
                    ]
                )
        return text

    def get_page_content(self, export_data: Dict[str, Any]) -> str:
        content = ""
        for export_data_entry in export_data["boxes"]:
            if export_data_entry["type"] in [
                BoxType.FLOWING_TEXT,
                BoxType.HEADING_TEXT,
                BoxType.PULLOUT_TEXT,
                BoxType.VERTICAL_TEXT,
                BoxType.CAPTION_TEXT,
            ]:
                ocr_result_block: OCRResultBlock = export_data_entry.get(
                    "ocr_results", []
                )
                content += self.get_text(ocr_result_block)
        return content
