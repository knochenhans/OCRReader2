import os
from datetime import datetime
from typing import Dict, Optional
from bs4 import BeautifulSoup, Tag
from ocr_engine.ocr_result import (  # type: ignore
    OCRResultBlock,
)
from page.box_type import BoxType  # type: ignore
from exporter.exporter import Exporter  # type: ignore
from loguru import logger


class ExporterHTMLSimple(Exporter):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.extension = "html"
        self.scaling_factor = 1.0
        self.soup: Optional[BeautifulSoup] = None
        self.body: Optional[Tag] = None

    def export_project(self, project_export_data: Dict) -> None:
        logger.info(f"Exporting to HTML directory: {self.output_path}")
        try:
            self.soup = BeautifulSoup(
                "<!DOCTYPE html><head></head><body></body></html>", "html.parser"
            )
            self.body = self.soup.body

            for page_export_data in project_export_data["pages"]:
                self.export_page(page_export_data)

            with open(self.get_output_path(), "w") as f:
                f.write(str(self.soup))
        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")

    def export_page(self, export_data: Dict) -> None:
        try:
            if self.body is not None and self.soup is not None:
                for export_data_entry in export_data["boxes"]:
                    box_type = export_data_entry.get("type", None)
                    match box_type:
                        case (
                            BoxType.FLOWING_TEXT
                            | BoxType.HEADING_TEXT
                            | BoxType.PULLOUT_TEXT
                            | BoxType.VERTICAL_TEXT
                            | BoxType.CAPTION_TEXT
                        ):
                            tag_name = "p"
                            if box_type == BoxType.HEADING_TEXT:
                                tag_name = "h1"
                            element = self.soup.new_tag(tag_name)
                            element["id"] = export_data_entry["id"]
                            element.string = export_data_entry.get("user_text", "")
                            self.body.append(element)
            else:
                logger.error("Failed to find body tag in HTML.")
        except Exception as e:
            logger.error(f"Failed to export page to HTML: {e}")
