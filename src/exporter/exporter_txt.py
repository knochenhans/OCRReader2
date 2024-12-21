from typing import Dict
from loguru import logger

from src.exporter.exporter import Exporter


class ExporterTxt(Exporter):
    def export(self, export_data: Dict) -> None:
        logger.info(f"Exporting to TXT file: {self.output_path}")
        try:
            with open(self.output_path, "w") as f:
                for export_data_entry in export_data["boxes"]:
                    if export_data_entry["type"] == "text":
                        logger.info(
                            f"Exporting text of box {export_data_entry['text']}"
                        )
                        f.write(f"{export_data_entry['text']}\n")
        except Exception as e:
            logger.error(f"Failed to export to TXT: {e}")
