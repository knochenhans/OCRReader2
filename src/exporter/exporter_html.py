import os
from datetime import datetime
from typing import Dict
from bs4 import BeautifulSoup, Tag
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultParagraph,
    OCRResultLine,
    OCRResultWord,
)
from src.page.ocr_box import BoxType
from src.exporter.exporter import Exporter
from loguru import logger


class ExporterHTML(Exporter):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.scaling_factor = 1.0

    def export_project(self, export_data: Dict) -> None:
        logger.info(f"Exporting to HTML directory: {self.output_path}")
        try:
            soup = BeautifulSoup(
                "<!DOCTYPE html><head></head><body></body></html>", "html.parser"
            )
            head = soup.head
            body = soup.body

            # Add stylesheet for position: absolute
            style_tag = soup.new_tag("style")
            style_tag.string = """
            .box {
                position: absolute;
                margin: 0;
            }
            .box p {
                white-space: pre-line;
                display: inline-block;
                margin: 0;
            }
            """

            if head is not None:
                head.append(style_tag)
            else:
                logger.error("Failed to find head tag in HTML.")

            ppi = export_data["page"].get("ppi", 300)

            if body is not None:
                for export_data_entry in export_data["boxes"]:
                    div = soup.new_tag("div")
                    div["class"] = "box"
                    div["id"] = export_data_entry["id"]

                    # Apply position to div
                    position = export_data_entry.get("position", {})
                    top = self.pixel_to_cm(
                        position.get("y", 0) * self.scaling_factor, ppi
                    )
                    left = self.pixel_to_cm(
                        position.get("x", 0) * self.scaling_factor, ppi
                    )
                    width = self.pixel_to_cm(
                        position.get("width", 0) * self.scaling_factor, ppi
                    )
                    height = self.pixel_to_cm(
                        position.get("height", 0) * self.scaling_factor, ppi
                    )
                    div["style"] = (
                        f"top: {top}cm; left: {left}cm; width: {width}cm; height: {height}cm;"
                    )

                    box_type = export_data_entry.get("type", None)
                    match box_type:
                        case (
                            BoxType.FLOWING_TEXT
                            | BoxType.HEADING_TEXT
                            | BoxType.PULLOUT_TEXT
                            | BoxType.VERTICAL_TEXT
                            | BoxType.CAPTION_TEXT
                        ):
                            tag = export_data_entry.get("tag", "")
                            ocr_result_block: OCRResultBlock = export_data_entry.get(
                                "ocr_results", []
                            )

                            if tag != "":
                                if tag.startswith("h") and tag[1:].isdigit():
                                    tag = f"h{int(tag[1:])}"
                                else:
                                    tag = "p"

                            else:
                                match box_type:
                                    case (
                                        BoxType.FLOWING_TEXT
                                        | BoxType.PULLOUT_TEXT
                                        | BoxType.VERTICAL_TEXT
                                    ):
                                        tag = "p"
                                    case BoxType.HEADING_TEXT:
                                        tag = "h1"
                                    case BoxType.CAPTION_TEXT:
                                        tag = "caption"
                            self.add_text(soup, div, ocr_result_block, tag)

                        case (
                            BoxType.FLOWING_IMAGE
                            | BoxType.HEADING_IMAGE
                            | BoxType.PULLOUT_IMAGE
                        ):
                            logger.info(
                                f"Exporting image of box {export_data_entry['id']}"
                            )
                            img = soup.new_tag("img")
                            img["src"] = self.save_cropped_image(
                                export_data["page"]["image_path"],
                                position.get("x", 0),
                                position.get("y", 0),
                                position.get("width", 0),
                                position.get("height", 0),
                                os.path.join(
                                    self.output_path, f"{export_data_entry['id']}.jpg"
                                ),
                            )
                            img["style"] = (
                                "width: 100%; height: 100%; object-fit: contain;"  # Adjust object-fit as needed
                            )
                            div.append(img)

                        case BoxType.VERT_LINE:
                            logger.info(
                                f"Exporting vertical line of box {export_data_entry['id']}"
                            )
                            div["style"] += "border-left: 1px solid black;"

                        case BoxType.HORZ_LINE:
                            logger.info(
                                f"Exporting horizontal line of box {export_data_entry['id']}"
                            )
                            div["style"] += "border-top: 1px solid black;"

                        case BoxType.EQUATION:
                            logger.info(
                                f"Exporting equation of box {export_data_entry['id']}"
                            )
                            ocr_result_block: OCRResultBlock = export_data_entry.get(
                                "ocr_results", []
                            )
                            self.add_text(soup, div, ocr_result_block, "p")
                    body.append(div)
            else:
                logger.error("Failed to find body tag in HTML.")

            output_file = os.path.join(self.output_path, self.filename)

            with open(output_file, "w") as f:
                f.write(str(soup))
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")

    def add_text(
        self,
        soup: BeautifulSoup,
        div: Tag,
        ocr_result_block: OCRResultBlock,
        tag: str,
    ) -> None:
        if ocr_result_block:
            for ocr_result_paragraph in ocr_result_block.paragraphs:
                text = "\n".join(
                    [
                        " ".join([word.text for word in line.words])
                        for line in ocr_result_paragraph.lines
                    ]
                )
                mean_font_size = self.find_mean_font_size(ocr_result_paragraph)
                new_tag = soup.new_tag(tag)
                new_tag.string = text
                new_tag["style"] = f"font-size: {mean_font_size}pt;"
                div.append(new_tag)
