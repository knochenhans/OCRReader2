from typing import List, Optional
import uuid

from loguru import logger
from project.project_settings import ProjectSettings # type: ignore
from exporter.exporter_html import ExporterHTML # type: ignore
from exporter.exporter_txt import ExporterTxt # type: ignore
from exporter.exporter_odt import ExporterODT # type: ignore
from exporter.exporter_epub import ExporterEPUB # type: ignore
from page.page import Page # type: ignore
from papersize import SIZES, parse_length # type: ignore
from pypdf import PdfReader

from enum import Enum, auto


class ExporterType(Enum):
    TXT = auto()
    HTML = auto()
    ODT = auto()
    EPUB = auto()


EXPORTER_MAP = {
    ExporterType.TXT: ExporterTxt,
    ExporterType.HTML: ExporterHTML,
    ExporterType.ODT: ExporterODT,
    ExporterType.EPUB: ExporterEPUB,
}


class Project:
    version = 4

    def __init__(self, name, description) -> None:
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.pages: List[Page] = []
        self.project_folder = ""
        self.settings = ProjectSettings(
            {
                "ppi": 300,
                "langs": ["eng"],
                "paper_size": "a4",
                "export_scaling_factor": 1.2,
                "export_path": "",
            }
        )

    def calculate_ppi(self, image, paper_size) -> int:
        # TODO: Let's assume 1:1 pixel ratio for now, so ignore width
        height_in = int(parse_length(SIZES[paper_size].split(" x ")[1], "in"))
        height_px = image.shape[0]
        return int(height_px / height_in)

    def add_image(self, image_path: str):
        logger.info(f"Adding image: {image_path}")
        self.add_page(Page(image_path))

    def add_images(self, image_paths: List[str]):
        for image_path in image_paths:
            self.add_image(image_path)

    def add_page(self, page: Page, index: Optional[int] = None):
        page.set_settings(self.settings)
        ppi = self.calculate_ppi(page.image, self.settings.get("paper_size"))
        page.settings.set("ppi", ppi)
        if index is None:
            self.pages.append(page)
        else:
            self.pages.insert(index, page)
        self.update_order()

    def remove_page(self, index: int):
        self.pages.pop(index)
        self.update_order()

    def get_page(self, index: int) -> Page:
        return self.pages[index]

    def get_page_count(self) -> int:
        return len(self.pages)

    def analyze_pages(self):
        for page in self.pages:
            logger.info(f"Analyzing page: {page.image_path}")
            page.analyze_page()

    def recognize_page_boxes(self):
        for page in self.pages:
            logger.info(f"Recognizing boxes for page: {page.image_path}")
            page.recognize_boxes()

    def set_settings(self, settings: ProjectSettings):
        self.settings = settings

    def import_pdf(self, pdf_path: str, from_page: int = 0, to_page: int = -1):
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
                logger.info(f"Added image: {image_path}")
        logger.info(f"Finished importing PDF: {pdf_path}")

    def export(self, exporter_type: ExporterType):
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

    def to_dict(self) -> dict:
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
    def from_dict(cls, data: dict) -> "Project":
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

    def sort_pages(self, key=lambda page: page.order, reverse=False) -> None:
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
