from typing import Dict
from bs4 import BeautifulSoup
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultParagraph,
    OCRResultLine,
    OCRResultWord,
)
from src.exporter.exporter import Exporter
from loguru import logger


class ExporterHTML(Exporter):
    def __init__(self, output_path: str) -> None:
        super().__init__(output_path)
        self.scaling_factor = 1.0

    def export(self, export_data: Dict) -> None:
        logger.info(f"Exporting to HTML file: {self.output_path}")
        try:
            soup = BeautifulSoup("<html><body></body></html>", "html.parser")
            body = soup.body

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
                        f"position: absolute; top: {top}cm; left: {left}cm; width: {width}cm; height: {height}cm;"
                    )

                    match export_data_entry["type"]:
                        case "text":
                            tag = export_data_entry.get("tag", "p")

                            if tag.startswith("h") and tag[1:].isdigit():
                                tag = f"h{int(tag[1:])}"
                            else:
                                tag = "p"
                            # text = export_data_entry["text"]

                            ocr_result_block: OCRResultBlock = export_data_entry.get(
                                "ocr_results", []
                            )
                            if ocr_result_block:
                                for ocr_result_paragraph in ocr_result_block.paragraphs:
                                    text = "\n".join(
                                        [
                                            " ".join([word.text for word in line.words])
                                            for line in ocr_result_paragraph.lines
                                        ]
                                    )
                                    mean_font_size = self.find_mean_font_size(
                                        ocr_result_paragraph
                                    )
                                    new_tag = soup.new_tag(tag)
                                    new_tag.string = text
                                    new_tag["style"] = (
                                        f"white-space: pre-line; font-size: {mean_font_size}pt;"
                                    )
                                    div.append(new_tag)

                        case "image":
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
                                f"{self.output_path}_{export_data_entry['id']}.jpg",
                            )
                            img["style"] = (
                                "width: 100%; height: 100%; object-fit: contain;"  # Adjust object-fit as needed
                            )
                            div.append(img)

                        case "vertical_line":
                            logger.info(
                                f"Exporting vertical line of box {export_data_entry['id']}"
                            )
                            div["style"] += "border-left: 1px solid black;"
                        case "horizontal_line":
                            logger.info(
                                f"Exporting horizontal line of box {export_data_entry['id']}"
                            )
                            div["style"] += "border-top: 1px solid black;"
                    body.append(div)
            else:
                logger.error("Failed to find body tag in HTML.")

            with open(self.output_path, "w") as f:
                f.write(soup.prettify())
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")
