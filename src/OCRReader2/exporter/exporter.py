import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pathvalidate import sanitize_filename
from PIL import Image
from SettingsManager import SettingsManager

from OCRReader2.ocr_edit_dialog.line_break_helper import LineBreakHelper
from OCRReader2.ocr_engine.ocr_result import OCRResultBlock, OCRResultParagraph
from OCRReader2.page.box_type import BoxType


class Exporter(ABC):
    def __init__(
        self, output_path: str, filename: str, application_settings: SettingsManager
    ) -> None:
        self.output_path: str = output_path
        self.filename: str = sanitize_filename(filename)

        self.application_settings: SettingsManager = application_settings

        self.extension: str = ""
        self.project_export_data: Dict[str, Any] = {}
        self.images: Dict[str, Dict[str, str]] = {}
        self.scaling_factor: float = 1

    @abstractmethod
    def export_project(self, project_export_data: Dict[str, Any]) -> None:
        self.project_export_data = project_export_data

        os.makedirs(self.output_path, exist_ok=True)

    def get_output_path(self) -> str:
        return os.path.join(self.output_path, (self.filename + "." + self.extension))

    def export_page(self, page_export_data: Dict[str, Any]) -> None:
        pass

    # def export_box(self, box_export_data: Dict[str, Any]) -> str:
    #     return ""

    def pixel_to_cm(self, pixels: int, ppi: int, rasterize: int = 2) -> float:
        return round(pixels / ppi * 2.54, rasterize)

    def save_cropped_image(
        self,
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
        image_name: str = "",
    ) -> str:
        image: Image.Image = Image.open(image_path)
        cropped_image: Image.Image = image.crop((x, y, x + width, y + height))
        cropped_image.save(output_path)

        if image_name == "":
            image_name = f"image_{len(self.images)}"

        image_info: Dict[str, str] = {
            "path": output_path,
            "name": image_name,
            "id": image_name,
        }

        self.images[image_name] = image_info
        return output_path

    def find_mean_font_size_paragraph(
        self, ocr_result_paragraph: OCRResultParagraph, rasterize: int = 0
    ) -> float:
        total_font_size: float = 0
        total_words: int = 0
        for line in ocr_result_paragraph.lines:
            for word in line.words:
                total_font_size += word.word_font_attributes["pointsize"]
                total_words += 1
        return round(total_font_size / total_words, rasterize)

    def find_mean_font_size(
        self, ocr_result_block: OCRResultBlock, rasterize: int = 0
    ) -> float:
        total_font_size: float = 0
        total_words: int = 0
        for paragraph in ocr_result_block.paragraphs:
            for line in paragraph.lines:
                for word in line.words:
                    total_font_size += word.word_font_attributes["pointsize"]
                    total_words += 1
        return round(total_font_size / total_words, rasterize)

    def get_text(
        self,
        ocr_result_block: Optional[OCRResultBlock],
    ) -> str:
        text: str = ""
        if ocr_result_block:
            text = ocr_result_block.get_text()
        return text

    def get_page_content(self, export_data: Dict[str, Any]) -> str:
        content: str = ""
        for export_data_entry in export_data["boxes"]:
            if export_data_entry["type"] in [
                BoxType.FLOWING_TEXT,
                BoxType.HEADING_TEXT,
                BoxType.PULLOUT_TEXT,
                BoxType.VERTICAL_TEXT,
                BoxType.CAPTION_TEXT,
            ]:
                ocr_result_block: Optional[OCRResultBlock] = export_data_entry.get(
                    "ocr_results", None
                )
                if ocr_result_block:
                    content += self.get_text(ocr_result_block)
        return content

    def merge_boxes(
        self, boxes: List[Dict[str, Any]], lang: str
    ) -> List[Dict[str, Any]]:
        merged_boxes: List[Dict[str, Any]] = []

        line_break_helper = LineBreakHelper(lang)

        for box_export_data in boxes:
            user_text = box_export_data.get("user_text", "")
            previous_box = merged_boxes[-1] if merged_boxes else None
            if previous_box:
                previous_box_text = previous_box.get("user_text", "")
                previous_box_flows_into_next = previous_box.get(
                    "flows_into_next", False
                )
                previous_box_type = previous_box.get("type", None)

                if previous_box_type is not None:
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
                        first_word = user_text.split()[0] if user_text else ""

                        if last_word.endswith("-"):
                            # TODO: How to handle hyphenated words which are not in the dictionary and split sentences (not ending with a hyphen)?
                            if line_break_helper.check_spelling(
                                last_word.rstrip()[:-1] + first_word.lstrip()
                            ):
                                previous_box["user_text"] = (
                                    previous_box_text.rstrip()[:-1] + user_text.lstrip()
                                )
                                previous_box["user_data"] = previous_box.get(
                                    "user_data", ""
                                )
                                continue
                        else:
                            previous_box["user_text"] = previous_box_text + user_text
                            previous_box["user_data"] = previous_box.get(
                                "user_data", ""
                            )
                            continue

            merged_boxes.append(box_export_data)
        return merged_boxes

    def limit_font_size(self, font_size: float) -> float:
        max_font_size = self.application_settings.get("max_font_size", 0)
        min_font_size = self.application_settings.get("min_font_size", 0)
        round_font_size = self.application_settings.get("round_font_size", 0)

        if max_font_size > 0 and font_size > max_font_size:
            font_size = max_font_size
        if min_font_size > 0 and font_size < min_font_size:
            font_size = min_font_size
        if round_font_size > 0:
            font_size = round(font_size / round_font_size) * round_font_size
        return font_size
