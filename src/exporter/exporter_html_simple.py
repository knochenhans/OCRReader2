import os
import shutil
from typing import Any, Dict

from iso639 import Lang
from loguru import logger

from exporter.exporter_html_based import ExporterHTMLBased  # type: ignore
from settings.settings import Settings  # type: ignore


class ExporterHTMLSimple(ExporterHTMLBased):
    def __init__(
        self, output_path: str, filename: str, application_settings: Settings
    ) -> None:
        super().__init__(output_path, filename, application_settings)
        self.extension = "html"
        self.scaling_factor = 1.0

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        super().export_project(project_export_data)

        logger.info(f"Exporting to HTML directory: {self.output_path}")

        lang = Lang(project_export_data["settings"]["langs"][0]).pt1

        try:
            section_index = 0
            html_content = self.get_html_header(project_export_data["name"], lang)

            boxes = []

            for page_export_data in self.project_export_data["pages"]:
                for box_export_data in page_export_data["boxes"]:
                    boxes.append(box_export_data)

            first_block = True
            for box_export_data in self.merge_boxes(boxes, lang):
                new_content, new_section = self.get_box_content(box_export_data)

                if new_section and not first_block and html_content.strip():
                    self.write_html_file(html_content, section_index)
                    section_index += 1
                    html_content = self.get_html_header(
                        project_export_data["name"], lang
                    )

                html_content += new_content
                first_block = False

            if html_content.strip():
                self.write_html_file(html_content, section_index)

            first_page_image = self.project_export_data["pages"][0]["image_path"]
            if first_page_image:
                _, extension = os.path.splitext(first_page_image)
                first_page_image_path = os.path.join(
                    self.output_path, f"image{extension}"
                )
                shutil.copyfile(first_page_image, first_page_image_path)
                logger.info(f"Copied image as: {first_page_image_path}")

        except Exception as e:
            logger.error(f"Failed to export to HTML: {e}")

    def get_html_header(self, title: str, lang: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                p {{
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body>
        """

    def write_html_file(self, html_content: str, section_index: int) -> None:
        html_content += """
        </body>
        </html>
        """
        output_file = os.path.join(
            self.output_path, f"{self.filename}_section_{section_index}.html"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Written section {section_index} to {output_file}")
