from typing import Dict
from bs4 import BeautifulSoup
from src.ocr_engine.exporter import Exporter
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
                    top = self.pixel_to_cm(position.get("y", 0) * self.scaling_factor, ppi)
                    left = self.pixel_to_cm(position.get("x", 0) * self.scaling_factor, ppi)
                    width = self.pixel_to_cm(position.get("width", 0) * self.scaling_factor, ppi)
                    height = self.pixel_to_cm(position.get("height", 0) * self.scaling_factor, ppi)
                    div["style"] = (
                        f"position: absolute; top: {top}cm; left: {left}cm; width: {width}cm; height: {height}cm;"
                    )

                    match export_data_entry["type"]:
                        case "text":
                            tag = export_data_entry.get("tag", "p")
                            text = export_data_entry["text"]
                            logger.info(
                                f"Exporting text of box {export_data_entry['id']}: {text}"
                            )
                            if tag in ["p", "h1", "h2", "h3", "h4", "h5", "h6"]:
                                new_tag = soup.new_tag(tag)
                            else:
                                new_tag = soup.new_tag("p")
                            new_tag.string = text
                            new_tag["style"] = (
                                "white-space: pre-line;"  # Preserve line breaks
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
                    body.append(div)
            else:
                logger.error("Failed to find body tag in HTML.")

            with open(self.output_path, "w") as f:
                f.write(soup.prettify())
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")
