import os
import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

import numpy as np
from loguru import logger
from papersize import SIZES, parse_length  # type: ignore
from pypdf import PdfReader
from SettingsManager import SettingsManager
from SettingsManager.settings_manager import StorageTarget

from OCRReader2.exporter.exporter_epub import ExporterEPUB
from OCRReader2.exporter.exporter_html import ExporterHTML
from OCRReader2.exporter.exporter_html_simple import ExporterHTMLSimple
from OCRReader2.exporter.exporter_odt import ExporterODT
from OCRReader2.exporter.exporter_preview import ExporterPreview
from OCRReader2.exporter.exporter_txt import ExporterTxt
from OCRReader2.ocr_processor import OCRProcessor
from OCRReader2.page.page import Page


class ExporterType(Enum):
    TXT = auto()
    HTML = auto()
    HTML_SIMPLE = auto()
    ODT = auto()
    EPUB = auto()
    PREVIEW = auto()


EXPORTER_MAP: Dict[ExporterType, Any] = {
    ExporterType.TXT: ExporterTxt,
    ExporterType.HTML: ExporterHTML,
    ExporterType.HTML_SIMPLE: ExporterHTMLSimple,
    ExporterType.ODT: ExporterODT,
    ExporterType.EPUB: ExporterEPUB,
}


class Project:
    version = 4

    def __init__(self, name: str = "", description: str = "") -> None:
        self.uuid = str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.creation_date: Optional[datetime] = None
        self.modification_date: Optional[datetime] = None
        self.pages: List[Page] = []
        self.folder: str = ""
        self.settings_manager: Optional[SettingsManager] = None
        self.ocr_processor: Optional[OCRProcessor] = None

    def calculate_ppi(
        self, image: Optional[np.ndarray[Any, Any]], paper_size: str
    ) -> int:
        if image is None or not hasattr(image, "shape"):
            return 0

        # Assume 1:1 pixel ratio for now, so ignore width
        height_in = int(parse_length(SIZES[paper_size].split(" x ")[1], "in"))
        height_px = image.shape[0]
        return int(height_px / height_in)

    def add_image(self, image_path: str) -> None:
        image_path = os.path.abspath(image_path)

        if not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            return

        if self.add_page(Page(image_path)):
            logger.success(f"Added image: {image_path}")
        else:
            logger.error(f"Failed to add image: {image_path}")

    def add_images(self, image_paths: List[str]) -> None:
        for image_path in image_paths:
            self.add_image(image_path)

    def add_page(self, page: Page, index: Optional[int] = None) -> bool:
        if any(
            existing_page.image_path == page.image_path for existing_page in self.pages
        ):
            logger.error(f"Page image already exists: {page.image_path}, skipping")
            return False

        if index is None:
            self.pages.append(page)
        else:
            self.pages.insert(index, page)
        self.update_order()
        return True

    def set_ocr_processor(self, ocr_processor: OCRProcessor) -> None:
        self.ocr_processor = ocr_processor

        for page in self.pages:
            page.ocr_processor = ocr_processor

    def remove_page(self, index: int) -> None:
        self.pages.pop(index)
        self.update_order()

    def get_page(self, index: int) -> Page:
        return self.pages[index]

    def get_page_count(self) -> int:
        return len(self.pages)

    def analyze_pages(self) -> None:
        for page in self.pages:
            logger.info(f"Analyzing page: {page.image_path}")

            if self.settings_manager:
                page.analyze_page(self.settings_manager)

    def recognize_page_boxes(self) -> None:
        for page in self.pages:
            logger.info(f"Recognizing boxes for page: {page.image_path}")

            page.recognize_ocr_boxes()

    def import_pdf(
        self,
        pdf_path: str,
        from_page: int = 0,
        to_page: int = -1,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> None:
        logger.info(
            f"Importing PDF: {pdf_path}, from_page: {from_page}, to_page: {to_page}"
        )

        pdf_reader = PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)
        if to_page == -1 or to_page >= total_pages:
            to_page = total_pages - 1

        for i in range(from_page, to_page + 1):
            logger.info(f"Importing PDF page: {i} / {total_pages}")
            page = pdf_reader.pages[i]
            for image in page.images:
                # Write image to project folder
                pdf_file_name = pdf_path.split("/")[-1].split(".")[0]
                project_folder = self.folder
                image_path = f"{project_folder}/{pdf_file_name}_{i}_{image.name}"

                with open(image_path, "wb") as f:
                    f.write(image.data)
                self.add_image(image_path)
                logger.success(f"Added PDF image: {image_path}")

            if progress_callback:
                progress_callback(
                    i - from_page + 1,
                    to_page - from_page + 1,
                    f"Importing PDF page: {i}",
                )

        logger.success(f"Finished importing PDF: {pdf_path}")

    def export(
        self, exporter_type: ExporterType, application_settings: SettingsManager
    ) -> None:
        if self.settings_manager:
            export_path = self.settings_manager.get("export_path")

            project_export_data: Dict[str, Any] = {
                "name": self.name,
                "description": self.description,
                "pages": [
                    page.generate_page_export_data(self.settings_manager)
                    for page in self.pages
                ],
                "settings": self.settings_manager.to_dict(),
            }

            exporter = EXPORTER_MAP[exporter_type](
                export_path, f"{self.name}", application_settings
            )
            exporter.export_project(project_export_data)

    def export_preview(self, application_settings: SettingsManager) -> None:
        if self.settings_manager:
            export_path = self.settings_manager.get("export_preview_path")
            if not export_path:
                logger.error("Export preview path is not set")
                return

            project_export_data: Dict[str, Any] = {
                "name": self.name,
                "description": self.description,
                "pages": [
                    page.generate_page_export_data(self.settings_manager)
                    for page in self.pages
                ],
                "settings": self.settings_manager.to_dict(),
            }

            exporter = ExporterPreview(
                export_path, f"{self.name}", application_settings
            )
            exporter.export_project(project_export_data)

    def to_dict(self) -> Dict[str, Any]:
        self.modification_date = datetime.now()
        return {
            "project": {
                "version": self.version,
                "uuid": self.uuid,
                "name": self.name,
                "description": self.description,
                "creation_date": (
                    self.creation_date.isoformat() if self.creation_date else None
                ),
                "modification_date": (
                    self.modification_date.isoformat()
                    if self.modification_date
                    else None
                ),
                "pages": [page.to_dict() for page in self.pages],
                "settings": (
                    self.settings_manager.to_dict() if self.settings_manager else None
                ),
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], folder: str) -> "Project":
        project_data = data.get("project", {})

        # Check version
        if project_data.get("version", 1) != cls.version:
            raise ValueError(
                f"Unsupported project version: {project_data.get('version', 'unknown')}, current version: {cls.version}"
            )

        project = cls()
        project.folder = folder
        project.uuid = project_data.get("uuid", str(uuid.uuid4()))
        project.name = project_data.get("name", "Untitled Project")
        project.description = project_data.get("description", "")
        project.creation_date = project_data.get(
            "creation_date"
        ) and datetime.fromisoformat(project_data.get("creation_date", ""))
        project.modification_date = project_data.get(
            "modification_date"
        ) and datetime.fromisoformat(project_data.get("modification_date", ""))
        project.pages = [
            Page.from_dict(page_data) for page_data in project_data.get("pages", [])
        ]
        project.settings_manager = (
            SettingsManager.from_dict(
                project_data["settings"],
                "project_settings",
                project.folder,
                target=StorageTarget.DATA,
            )
            if project_data.get("settings")
            else None
        )

        return project

    def sort_pages(self, key=lambda page: page.order, reverse: bool = False) -> None:
        self.pages.sort(key=key, reverse=reverse)
        self.update_order()

    def move_page(self, index: int, new_index: int) -> None:
        page_to_move = self.pages.pop(index)
        self.pages.insert(new_index, page_to_move)
        self.update_order()

    def replace_page(self, index: int, page: Page) -> None:
        self.pages[index] = page
        self.update_order()

    def update_order(self) -> None:
        for index, page in enumerate(self.pages):
            page.order = index

    def __len__(self) -> int:
        return len(self.pages)

    def __iter__(self):
        return iter(self.pages)

    def __getitem__(self, index: int) -> Page:
        return self.pages[index]

    def __setitem__(self, index: int, page: Page) -> None:
        self.pages[index] = page
        self.update_order()

    def __delitem__(self, index: int) -> None:
        self.pages.pop(index)
        self.update_order()

    def __str__(self) -> str:
        return f"Project(name={self.name}, description={self.description}, pages={self.pages}, uuid={self.uuid})"

    def __repr__(self) -> str:
        return self.__str__()
