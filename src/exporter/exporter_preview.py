import os
from datetime import datetime
from typing import Any, Dict
from exporter.exporter_html_based import ExporterHTMLBased  # type: ignore
from loguru import logger
from iso639 import Lang  # type: ignore


class ExporterPreview(ExporterHTMLBased):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.pages: list = []

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        super().export_project(project_export_data)

        logger.info(f"Generating HTML preview: {self.output_path}")

        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="{Lang(self.project_export_data["settings"]["langs"][0]).pt1}">
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

            for page_export_data in self.project_export_data["pages"]:
                html_content += self.export_page(page_export_data)

            html_content += """
            </body>
            </html>
            """

            output_file = os.path.join(self.output_path, self.filename)
            with open(output_file + ".html", "w", encoding="utf-8") as f:
                f.write(html_content)

        except Exception as e:
            logger.error(f"Failed to generate HTML preview: {e}")

    def export_page(self, page_export_data: Dict) -> str:
        super().export_page(page_export_data)

        try:
            page_content = f"""
            <div class="page" id="page_{page_export_data["order"]}">
                <h2>Page {page_export_data["order"]}</h2>
                {self.get_page_content(page_export_data)}
            </div>
            """
            return page_content

        except Exception as e:
            logger.error(f"Failed to export page: {e}")
            return ""
