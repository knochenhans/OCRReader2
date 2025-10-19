import os
import shutil
from typing import List, Optional

from loguru import logger
from PIL import Image

from ocr_engine.ocr_result import OCRResultLine
from project.project import Project


class LineExporter:
    def __init__(self, project: Project, train_data_path: str = ""):
        self.train_data_path = train_data_path
        self.project = project
        self.confidence_threshold = 0

    def export_project_lines(
        self,
        confidence_threshold: int = 80,
        max_lines: Optional[int] = None,
        box_ids: Optional[List] = None,
        remove_existing: bool = False,  # New parameter to remove existing files
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.box_ids = box_ids

        # Remove existing files if the option is enabled
        if remove_existing:
            self._remove_existing_files()

        lines_exported = 0

        for p, page in enumerate(self.project.pages):
            lines_exported += self._process_page(p, page, max_lines, lines_exported)
            if max_lines is not None and lines_exported >= max_lines:
                logger.info(f"Reached max_lines limit: {max_lines}")
                break

    def export_page_lines(
        self, page_index: int, confidence_threshold: int = 80
    ) -> None:
        self.confidence_threshold = confidence_threshold

        page = self.project.pages[page_index]
        ocr_boxes = page.layout.ocr_boxes

        if page.image_path is None:
            logger.warning(
                f"Image path is None for page {page_index}. Skipping line export."
            )
            return

        for b, box in enumerate(ocr_boxes):
            if self.box_ids is None or box.id in self.box_ids:
                if box.ocr_results:
                    for paragraph_index, paragraph in enumerate(
                        box.ocr_results.paragraphs
                    ):
                        for l, line in enumerate(paragraph.lines):
                            # Process line if confidence is below the threshold or threshold is 0
                            if (
                                self.confidence_threshold == 0
                                or line.confidence < self.confidence_threshold
                            ):
                                self._process_line(
                                    page_index,
                                    b,
                                    paragraph_index,
                                    l,
                                    line,
                                    page.image_path,
                                )

    def export_box_lines(
        self, box_index: int, image_path: str, confidence_threshold: int = 80
    ) -> None:
        self.confidence_threshold = confidence_threshold

        page_index = 0
        box = self.project.pages[page_index].layout.ocr_boxes[box_index]

        if box.ocr_results:
            for paragraph_index, paragraph in enumerate(box.ocr_results.paragraphs):
                for l, line in enumerate(paragraph.lines):
                    # Process line if confidence is below the threshold or threshold is 0
                    if (
                        self.confidence_threshold == 0
                        or line.confidence < self.confidence_threshold
                    ):
                        self._process_line(
                            page_index, box_index, paragraph_index, l, line, image_path
                        )

    def _process_page(
        self, page_index: int, page, max_lines: Optional[int], lines_exported: int
    ) -> int:
        ocr_boxes = page.layout.ocr_boxes
        lines_exported_from_page = 0

        for b, box in enumerate(ocr_boxes):
            if self.box_ids is None or box.id in self.box_ids:
                if box.ocr_results:
                    for paragraph_index, paragraph in enumerate(
                        box.ocr_results.paragraphs
                    ):
                        for l, line in enumerate(paragraph.lines):
                            # Stop if max_lines is reached
                            if (
                                max_lines is not None
                                and lines_exported + lines_exported_from_page
                                >= max_lines
                            ):
                                return lines_exported_from_page

                            # Process line if confidence is below the threshold or threshold is 0
                            if (
                                self.confidence_threshold == 0
                                or line.confidence < self.confidence_threshold
                            ):
                                self._process_line(
                                    page_index,
                                    b,
                                    paragraph_index,
                                    l,
                                    line,
                                    page.image_path,
                                )
                                lines_exported_from_page += 1

        return lines_exported_from_page

    def _process_line(
        self,
        page_index: int,
        box_index: int,
        paragraph_index: int,
        line_index: int,
        line: OCRResultLine,
        image_path: str,
    ) -> None:
        print(
            f"Page: {page_index}, Box: {box_index}, Paragraph: {paragraph_index}, Line: {line.get_text()}, Confidence: {line.confidence}"
        )

        if image_path is not None:
            self._save_cropped_image(
                page_index, box_index, paragraph_index, line_index, line, image_path
            )

        self._save_line_text(page_index, box_index, paragraph_index, line_index, line)

    def _save_cropped_image(
        self,
        page_index: int,
        box_index: int,
        paragraph_index: int,
        line_index: int,
        line,
        image_path: str,
    ) -> None:
        image = Image.open(image_path)

        if line.bbox is not None:
            cropped_image = image.crop(
                (line.bbox[0], line.bbox[1], line.bbox[2], line.bbox[3])
            )
            cropped_image_path = os.path.join(
                self.train_data_path,
                f"page_{page_index}_box_{box_index}_paragraph_{paragraph_index}_line_{line_index}.tif",
            )
            cropped_image.save(cropped_image_path, format="TIFF")
            logger.info(f"Cropped image saved to {cropped_image_path}")

    def _save_line_text(
        self,
        page_index: int,
        box_index: int,
        paragraph_index: int,
        line_index: int,
        line,
    ) -> None:
        line_text = line.get_text()

        line_text_path = os.path.join(
            self.train_data_path,
            f"page_{page_index}_box_{box_index}_paragraph_{paragraph_index}_line_{line_index}.gt.txt",
        )

        if not os.path.exists(line_text_path):
            with open(line_text_path, "w") as text_file:
                text_file.write(line_text)
            logger.info(f"Line text saved to {line_text_path}")
        else:
            logger.info(f"Line text already exists at {line_text_path}, skipping.")

    def _remove_existing_files(self) -> None:
        """
        Remove all existing files in the training data directory.
        """
        if os.path.exists(self.train_data_path):
            for file_name in os.listdir(self.train_data_path):
                file_path = os.path.join(self.train_data_path, file_name)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or symbolic link
                        logger.info(f"Removed file: {file_path}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove directory
                        logger.info(f"Removed directory: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")
