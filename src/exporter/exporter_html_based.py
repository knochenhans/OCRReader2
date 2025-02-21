import os
from datetime import datetime
from typing import Dict
from ocr_engine.ocr_result import (  # type: ignore
    OCRResultBlock,
)
from page.box_type import BoxType  # type: ignore
from exporter.exporter import Exporter  # type: ignore
from loguru import logger
from ebooklib import epub  # type: ignore
from iso639 import Lang  # type: ignore


class ExporterHTMLBased(Exporter):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)

    def export_project(self, project_export_data: Dict) -> None:
        super().export_project(project_export_data)

    def export_page(self, page_export_data: Dict) -> None:
        super().export_page(page_export_data)

    def add_block_text(
        self, ocr_result_block: OCRResultBlock, user_text: str, tag: str
    ) -> str:
        content = ""
        if ocr_result_block:
            for ocr_result_paragraph in ocr_result_block.paragraphs:
                if ocr_result_paragraph.user_text:
                    text = ocr_result_paragraph.user_text
                else:
                    text = "\n".join(
                        [
                            " ".join([word.text for word in line.words])
                            for line in ocr_result_paragraph.lines
                        ]
                    )
                mean_font_size = self.find_mean_font_size(ocr_result_paragraph)
                content += (
                    f'<{tag} style="font-size: {mean_font_size}pt;">{text}</{tag}>'
                )
        return content

    def get_page_content(self, page_data_entry: Dict) -> str:
        html_content = ""
        for box_data_entry in page_data_entry["boxes"]:
            html_content += self.get_box_content(
                box_data_entry, page_data_entry["image_path"]
            )
        return html_content

    def get_box_content(self, box_data_entry: Dict, image_path: str) -> str:
        match box_data_entry["type"]:
            case (
                BoxType.FLOWING_TEXT
                | BoxType.HEADING_TEXT
                | BoxType.PULLOUT_TEXT
                | BoxType.VERTICAL_TEXT
                | BoxType.CAPTION_TEXT
            ):
                ocr_result_block: OCRResultBlock = box_data_entry.get("ocr_results", [])
                user_text = box_data_entry.get("user_text", "")

                return self.add_block_text(ocr_result_block, user_text, "p")
            case BoxType.FLOWING_IMAGE | BoxType.HEADING_IMAGE | BoxType.PULLOUT_IMAGE:
                output_path = self.save_cropped_image(
                    image_path,
                    box_data_entry["position"]["x"],
                    box_data_entry["position"]["y"],
                    box_data_entry["position"]["width"],
                    box_data_entry["position"]["height"],
                    os.path.join(self.output_path, f"{box_data_entry['id']}.jpg"),
                )
                if os.path.exists(output_path):
                    ppi = self.project_export_data["settings"].get("ppi", 300)

                    # Calculate the scaling factor based on the PPI
                    scaling_factor = ppi / 72
                    width = box_data_entry["position"]["width"] / scaling_factor
                    height = box_data_entry["position"]["height"] / scaling_factor

                    filename = os.path.basename(output_path)

                    float_style = ""

                    if box_data_entry["type"] == BoxType.FLOWING_IMAGE:
                        float_style = "float: left;"

                    return f'<img src="static/{filename}" alt="Image {box_data_entry['id']}" width="{width}" height="{height}"  style="{float_style}">'
                else:
                    logger.warning(f"Image not found: {output_path}")
                    return '<img alt="Image not found">'
        return ""
