import os
from typing import Any, Dict, List

from iso639 import Lang
from loguru import logger
from SettingsManager import SettingsManager

from OCRReader2.exporter.exporter_html_based import ExporterHTMLBased


class ExporterPreview(ExporterHTMLBased):
    def __init__(
        self, output_path: str, filename: str, application_settings: SettingsManager
    ) -> None:
        super().__init__(output_path, filename, application_settings)
        self.pages: List[Lang] = []

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

            boxes: List[Dict[str, Any]] = []

            for page_export_data in self.project_export_data["pages"]:
                for box_data_entry in page_export_data["boxes"]:
                    boxes.append(box_data_entry)

            for box_data_entry in self.merge_boxes(boxes, lang):
                if box_data_entry["user_data"].get("class") == "section":
                    html_content += "<hr/>"
                new_content, _ = self.get_box_content(box_data_entry)
                html_content += new_content

            html_content += """
            </body>
            </html>
            """

            output_file = os.path.join(self.output_path, self.filename)

            with open(output_file + ".html", "w", encoding="utf-8") as f:
                f.write(html_content)

        except Exception as e:
            logger.error(f"Failed to generate HTML preview: {e}")
