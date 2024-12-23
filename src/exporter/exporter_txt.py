import os
from typing import Dict
from loguru import logger

from src.page.ocr_box import BoxType
from src.exporter.exporter import Exporter


class ExporterTxt(Exporter):
    def export_project(self, export_data: Dict) -> None:
        logger.info(f"Exporting to TXT file: {self.output_path}")
        try:
            filename = os.path.join(self.output_path, self.filename)
            with open(filename + ".txt", "w") as f:
                for export_data_entry in export_data["boxes"]:
                    if export_data_entry["type"] in [
                        BoxType.FLOWING_TEXT,
                        BoxType.HEADING_TEXT,
                        BoxType.PULLOUT_TEXT,
                        BoxType.VERTICAL_TEXT,
                        BoxType.CAPTION_TEXT,
                    ]:
                        logger.info(
                            f"Exporting text of box {self.get_text(export_data_entry["ocr_results"])}"
                        )
                        f.write(f"{self.get_text(export_data_entry['ocr_results'])}\n")
        except Exception as e:
            logger.error(f"Failed to export to TXT: {e}")
