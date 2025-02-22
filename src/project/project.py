from typing import List, Optional, Dict, Any
import uuid
import numpy as np  # type: ignore

from loguru import logger
from project.project_settings import ProjectSettings  # type: ignore
from exporter.exporter_html import ExporterHTML  # type: ignore
from exporter.exporter_txt import ExporterTxt  # type: ignore
from exporter.exporter_odt import ExporterODT  # type: ignore
from exporter.exporter_epub import ExporterEPUB  # type: ignore
from exporter.exporter_preview import ExporterPreview  # type: ignore
from page.page import Page  # type: ignore
from papersize import SIZES, parse_length  # type: ignore
from pypdf import PdfReader

from enum import Enum, auto
import os


class ExporterType(Enum):
    TXT = auto()
    HTML = auto()
    ODT = auto()
    EPUB = auto()
    PREVIEW = auto()


EXPORTER_MAP: Dict[ExporterType, Any] = {
    ExporterType.TXT: ExporterTxt,
    ExporterType.HTML: ExporterHTML,
    ExporterType.ODT: ExporterODT,
    ExporterType.EPUB: ExporterEPUB,
}


class Project:
    version = 4

    def __init__(self, name: str, description: str) -> None:
        self.uuid = str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.pages: List[Page] = []
        self.project_folder: str = ""
        self.settings: ProjectSettings = ProjectSettings(
            {
                "ppi": 300,
                "langs": ["eng"],
                "paper_size": "a4",
                "export_scaling_factor": 1.2,
                "export_path": "",
            }
        )

    def calculate_ppi(self, image: np.ndarray, paper_size: str) -> int:
        if image is None or not hasattr(image, "shape"):
            return 0

        # Assume 1:1 pixel ratio for now, so ignore width
        height_in = int(parse_length(SIZES[paper_size].split(" x ")[1], "in"))
        height_px = image.shape[0]
        return int(height_px / height_in)

    def add_image(self, image_path: str) -> None:
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
        page.set_settings(self.settings)

        if page.image is not None and hasattr(page.image, "shape"):
            ppi = self.calculate_ppi(page.image, self.settings.get("paper_size"))
            page.settings.set("ppi", ppi)

        if index is None:
            self.pages.append(page)
        else:
            self.pages.insert(index, page)
        self.update_order()
        return True

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
            page.analyze_page()

    def recognize_page_boxes(self) -> None:
        for page in self.pages:
            logger.info(f"Recognizing boxes for page: {page.image_path}")
            page.recognize_ocr_boxes()

    def set_settings(self, settings: ProjectSettings) -> None:
        self.settings = settings

    def import_pdf(self, pdf_path: str, from_page: int = 0, to_page: int = -1) -> None:
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
                project_folder = self.project_folder
                image_path = f"{project_folder}/{pdf_file_name}_{i}_{image.name}"

                with open(image_path, "wb") as f:
                    f.write(image.data)
                self.add_image(image_path)
                logger.success(f"Added PDF image: {image_path}")
        logger.success(f"Finished importing PDF: {pdf_path}")

    def export(self, exporter_type: ExporterType) -> None:
        export_path = self.settings.get("export_path")
        export_scaling_factor = self.settings.get("export_scaling_factor")

        langs = self.settings.get("langs") or ["eng"]

        project_export_data = {
            "name": self.name,
            "description": self.description,
            "pages": [page.generate_page_export_data() for page in self.pages],
            "settings": self.settings.to_dict(),
        }

        exporter = EXPORTER_MAP[exporter_type](export_path, f"{self.name}")
        exporter.scaling_factor = export_scaling_factor
        exporter.export_project(project_export_data)

    def export_preview(self) -> None:
        export_path = self.settings.get("export_preview_path")
        if not export_path:
            logger.error("Export preview path is not set")
            return

        project_export_data = {
            "name": self.name,
            "description": self.description,
            "pages": [page.generate_page_export_data() for page in self.pages],
            "settings": self.settings.to_dict(),
        }

        exporter = ExporterPreview(export_path, f"{self.name}")
        exporter.export_project(project_export_data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": {
                "version": self.version,
                "name": self.name,
                "description": self.description,
                "pages": [page.to_dict() for page in self.pages],
                "uuid": self.uuid,
                "settings": self.settings.to_dict(),
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        project_data = data["project"]

        # Check version
        if project_data.get("version", 1) != cls.version:
            raise ValueError(
                f"Unsupported project version: {project_data['version']}, current version: {cls.version}"
            )

        project = cls(project_data["name"], project_data["description"])
        project.uuid = project_data["uuid"]
        project.settings = ProjectSettings.from_dict(project_data["settings"])

        for page_data in project_data["pages"]:
            page = Page.from_dict(page_data, project.settings)
            project.add_page(page)

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
