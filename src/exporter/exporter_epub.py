import os
from datetime import datetime
from typing import Dict
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


class ExporterEPUB(Exporter):
    def __init__(self, output_path: str, filename: str) -> None:
        super().__init__(output_path, filename)
        self.scaling_factor = 1.0

    def export_project(self, project_export_data: Dict) -> None:
        logger.info(f"Exporting to EPUB: {self.output_path}")

        try:
            book = epub.EpubBook()
            book.set_identifier(project_export_data["name"])
            book.set_title(project_export_data["name"])
            book.set_language(Lang(project_export_data["lang"]).pt1)

            pages_data = project_export_data["pages"]

            # Create one chapter per page
            for page_data in pages_data:
                chapter = epub.EpubHtml(
                    title=f'Page {page_data["order"]}',
                    file_name=f'page_{page_data["order"]}.xhtml',
                    lang=Lang(project_export_data["lang"]).pt1,
                )

                div_content = ""

                page_content = self.get_page_content(page_data)

                div_content += f'<div class="page" style="width: 100%; height: 100%;">{page_content}</div>'

                chapter.content = div_content

                book.add_item(chapter)

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
            book.spine = ["nav"] + [
                f'page_{page_data["order"]}' for page_data in pages_data
            ]

            # Write to the file
            output_file = os.path.join(self.output_path, self.filename)
            epub.write_epub(output_file + ".epub", book, {})

        except Exception as e:
            logger.error(f"Failed to export to EPUB: {e}")

    def add_text(self, ocr_result_block: OCRResultBlock, tag: str) -> str:
        content = ""
        if ocr_result_block:
            for ocr_result_paragraph in ocr_result_block.paragraphs:
                text = "\n".join(
                    [
                        " ".join([word.text for word in line.words])
                        for line in ocr_result_paragraph.lines
                    ]
                )
                mean_font_size = self.find_mean_font_size(ocr_result_paragraph)
                content += (
                    f'<{tag} style="font-size: {mean_font_size}pt;">{text}</{tag}>'
                )
        return content

    def get_page_content(self, page_data: Dict) -> str:
        content = ""
        for export_data_entry in page_data["boxes"]:
            if export_data_entry["type"] in [
                BoxType.FLOWING_TEXT,
                BoxType.HEADING_TEXT,
                BoxType.PULLOUT_TEXT,
                BoxType.VERTICAL_TEXT,
                BoxType.CAPTION_TEXT,
            ]:
                ocr_result_block: OCRResultBlock = export_data_entry.get(
                    "ocr_results", []
                )
                content += self.get_text(ocr_result_block) + "<br>"
        return content
