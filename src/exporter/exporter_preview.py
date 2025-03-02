import os
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger
from iso639 import Lang

from exporter.exporter_html_based import ExporterHTMLBased  # type: ignore
from ocr_edit_dialog.line_break_helper import LineBreakHelper  # type: ignore
from page.box_type import BoxType  # type: ignore


class ExporterPreview(ExporterHTMLBased):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.pages: list = []

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        super().export_project(project_export_data)

        logger.info(f"Generating HTML preview: {self.output_path}")

        lang = Lang(project_export_data["settings"]["langs"][0]).pt1

        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="{lang}">
            <head>
                <meta charset="UTF-8">
                <title>{self.project_export_data["name"]}</title>
                <style>
                    p {{
                        font-family: Arial, sans-serif;
                    }}
                    img {{
                        margin-top: 10px;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
            """

            boxes = []

            for page_export_data in self.project_export_data["pages"]:
                for box_export_data in page_export_data["boxes"]:
                    boxes.append(box_export_data)

            for box_export_data in self.merge_boxes(boxes, lang):
                html_content += self.get_box_content(box_export_data)

            html_content += """
            </body>
            </html>
            """

            output_file = os.path.join(self.output_path, self.filename)
            with open(output_file + ".html", "w", encoding="utf-8") as f:
                f.write(html_content)

        except Exception as e:
            logger.error(f"Failed to generate HTML preview: {e}")
