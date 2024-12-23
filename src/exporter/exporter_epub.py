import os
from datetime import datetime
from typing import Dict
from src.exporter.exporter_html_based import ExporterHTMLBased
from src.ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultParagraph,
    OCRResultLine,
    OCRResultWord,
)
from src.page.ocr_box import BoxType
from src.exporter.exporter import Exporter
from loguru import logger
from ebooklib import epub
from iso639 import Lang


class ExporterEPUB(ExporterHTMLBased):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.scaling_factor = 1.0

    def export_project(self, project_export_data: Dict) -> None:
        super().export_project(project_export_data)
        logger.info(f"Exporting to EPUB: {self.output_path}")

        try:
            book = epub.EpubBook()
            book.set_identifier(project_export_data["name"])
            book.set_title(project_export_data["name"])
            book.set_language(Lang(project_export_data["settings"]["langs"][0]).pt1)

            css_content = """
            p {
                font-family: Arial, sans-serif;
            }

            img {
                margin-top: 10px;
                margin-bottom: 10px;
            }
            """

            default_css = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content=css_content.encode("utf-8"),
            )
            book.add_item(default_css)

            pages_data = project_export_data["pages"]

            pages = []

            # Create one chapter per page
            for page_data in pages_data:
                page = epub.EpubHtml(
                    title=f'Page {page_data["order"]}',
                    file_name=f'page_{page_data["order"]}.xhtml',
                    lang=Lang(page_data["lang"]).pt1,
                )

                page.content = f"<html><head></head><body>{self.get_page_content(page_data)}</body></html>"
                page.add_item(default_css)

                book.add_item(page)
                pages.append(page)

            for image in self.images.values():
                image_path = image["path"]
                image_name = image["name"]
                image_id = image["id"]

                if image_name == "":
                    image_name = os.path.basename(image_path)

                book.add_item(
                    epub.EpubItem(
                        uid=image_id,
                        file_name="static/" + os.path.basename(image_path),
                        media_type="image/jpeg",
                        content=open(image_path, "rb").read(),
                    )
                )

            # Define Table Of Contents
            book.toc = [
                epub.Link(
                    f'page_{page_data["order"]}.xhtml',
                    f'Page {page_data["order"]}',
                    f'page_{page_data["order"]}',
                )
                for page_data in pages_data
            ]

            # Add default NCX and Nav file
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Basic spine
            book.spine = ["nav", "style", *pages]

            # Write to the file
            output_file = os.path.join(self.output_path, self.filename)
            epub.write_epub(output_file + ".epub", book, {})

        except Exception as e:
            logger.error(f"Failed to export to EPUB: {e}")
