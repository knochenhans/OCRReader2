from typing import Dict
from loguru import logger
import mistune

from src.exporter.exporter import Exporter


class ExporterMD(Exporter):
    def export(self, export_data: Dict) -> None:
        logger.info(f"Exporting to MD file: {self.output_path}")
        try:
            markdown = mistune.create_markdown()
            with open(self.output_path, "w") as f:
                for export_data_entry in export_data["boxes"]:
                    if export_data_entry["type"] == "text":
                        tag = export_data_entry.get("tag", "p")
                        text = export_data_entry["text"]
                        logger.info(f"Exporting text of box: {text}")
                        if tag.startswith("h") and tag[1:].isdigit():
                            f.write(f"{'#' * int(tag[1:])} {text}\n")
                        else:
                            f.write(f"{text}\n")
        except Exception as e:
            logger.error(f"Failed to export to MD: {e}")
