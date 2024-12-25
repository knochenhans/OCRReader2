import os
from datetime import datetime
from typing import Any, Dict
from exporter.exporter_html_based import ExporterHTMLBased
from ocr_engine.ocr_result import (
    OCRResultBlock,
    OCRResultParagraph,
    OCRResultLine,
    OCRResultWord,
)
from page.box_type import BoxType
from exporter.exporter import Exporter
from loguru import logger
from ebooklib import epub # type: ignore
from iso639 import Lang # type: ignore


class ExporterEPUB(ExporterHTMLBased):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.scaling_factor: float = 1.0
        self.pages: list = []
        self.book: epub.EpubBook | None = None

    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        super().export_project(project_export_data)

        logger.info(f"Exporting to EPUB: {self.output_path}")

        try:
            self.book = epub.EpubBook()
            self.book.set_identifier(self.project_export_data["name"])
            self.book.set_title(self.project_export_data["name"])
            self.book.set_language(
                Lang(self.project_export_data["settings"]["langs"][0]).pt1
            )

            css_content = """
            p {
                font-family: Arial, sans-serif;
            }

            img {
                margin-top: 10px;
                margin-bottom: 10px;
            }
            """

            self.default_css = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content=css_content.encode("utf-8"),
            )
            self.book.add_item(self.default_css)

            for page_export_data in self.project_export_data["pages"]:
                self.export_page(page_export_data)

            for image in self.images.values():
                image_path = image["path"]
                image_name = image["name"]
                image_id = image["id"]

                if image_name == "":
                    image_name = os.path.basename(image_path)

                self.book.add_item(
                    epub.EpubItem(
                        uid=image_id,
                        file_name="static/" + os.path.basename(image_path),
                        media_type="image/jpeg",
                        content=open(image_path, "rb").read(),
                    )
                )

            # Define Table Of Contents
            self.book.toc = [
                epub.Link(
                    f'page_{page_data["order"]}.xhtml',
                    f'Page {page_data["order"]}',
                    f'page_{page_data["order"]}',
                )
                for page_data in self.project_export_data["pages"]
            ]

            # Add default NCX and Nav file
            self.book.add_item(epub.EpubNcx())
            self.book.add_item(epub.EpubNav())

            # Basic spine
            self.book.spine = ["nav", "style", *self.pages]

            # Write to the file
            output_file = os.path.join(self.output_path, self.filename)
            epub.write_epub(output_file + ".epub", self.book, {})

        except Exception as e:
            logger.error(f"Failed to export to EPUB: {e}")

    def export_page(self, page_export_data: Dict) -> None:
        super().export_page(page_export_data)

        try:
            # Create one chapter per page
            page = epub.EpubHtml(
                title=f'Page {page_export_data["order"]}',
                file_name=f'page_{page_export_data["order"]}.xhtml',
                lang=Lang(page_export_data["lang"]).pt1,
            )

            page.content = f"<html><head></head><body>{self.get_page_content(page_export_data)}</body></html>"
            page.add_item(self.default_css)

            if self.book is not None:
                self.book.add_item(page)
                self.pages.append(page)

        except Exception as e:
            logger.error(f"Failed to export to EPUB: {e}")
