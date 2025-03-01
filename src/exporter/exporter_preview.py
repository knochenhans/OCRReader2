import os
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger
from iso639 import Lang

from exporter.exporter_html_based import ExporterHTMLBased  # type: ignore
from line_break_editor.line_break_helper import LineBreakHelper  # type: ignore
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

    def merge_boxes(self, boxes: List, lang: str) -> List[Dict]:
        merged_boxes: List[Dict] = []

        line_break_helper = LineBreakHelper(lang)

        for box_export_data in boxes:
            box_text = box_export_data.get("user_text", "")
            previous_box = merged_boxes[-1] if merged_boxes else None
            if previous_box:
                previous_box_text = previous_box.get("user_text", "")
                previous_box_flows_into_next = previous_box.get(
                    "flows_into_next", False
                )
                previous_box_type = previous_box.get("type", None)

                if previous_box_flows_into_next and previous_box_type.value in [
                    BoxType.FLOWING_TEXT.value,
                    BoxType.HEADING_TEXT.value,
                    BoxType.PULLOUT_TEXT.value,
                    BoxType.VERTICAL_TEXT.value,
                    BoxType.CAPTION_TEXT.value,
                ]:
                    previous_box["flows_into_next"] = box_export_data.get(
                        "flows_into_next", False
                    )

                    last_word = (
                        previous_box_text.split()[-1] if previous_box_text else ""
                    )
                    first_word = box_text.split()[0] if box_text else ""

                    if last_word.endswith("-"):
                        if line_break_helper.check_spelling(
                            last_word.rstrip()[:-1] + first_word.lstrip()
                        ):
                            previous_box["user_text"] = (
                                previous_box_text.rstrip()[:-1] + box_text.lstrip()
                            )
                            continue
                    else:
                        previous_box["user_text"] = previous_box_text + box_text
                        continue

            merged_boxes.append(box_export_data)
        return merged_boxes

    def export_page(self, page_export_data: Dict) -> str:
        super().export_page(page_export_data)

        try:
            page_content = f"""
            <div class="page" id="page_{page_export_data["order"]}">
                {self.get_page_content(page_export_data)}
            </div>
            """
            return page_content

        except Exception as e:
            logger.error(f"Failed to export page: {e}")
            return ""

    # def export_box(self, box_export_data: Dict) -> str:
    #     if box_export_data.get("user_text") is None:
    #         return ""

    #     try:
    #         block_content = f"""
    #         <div class="box" id="{box_export_data["id"]}">
    #             {box_export_data["user_text"]}
    #         </div>
    #         """
    #         return block_content
    #     except Exception as e:
    #         logger.error(f"Failed to export block: {e}")
    #         return ""
