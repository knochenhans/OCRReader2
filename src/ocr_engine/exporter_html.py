from typing import Dict
from bs4 import BeautifulSoup
from src.ocr_engine.exporter import Exporter
from loguru import logger


class ExporterHTML(Exporter):
    def export(self, export_data: Dict) -> None:
        logger.info(f"Exporting to HTML file: {self.output_path}")
        try:
            soup = BeautifulSoup("<html><body></body></html>", "html.parser")
            body = soup.body

            if body is not None:
                for export_data_entry in export_data["boxes"]:
                    if export_data_entry["type"] == "text":
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
                        body.append(new_tag)
            else:
                logger.error("Failed to find body tag in HTML.")

            with open(self.output_path, "w") as f:
                f.write(soup.prettify())
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")
