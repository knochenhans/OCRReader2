from typing import List, Optional
import uuid

from loguru import logger
from project_settings import ProjectSettings
from src.exporter.exporter_html import ExporterHTML
from src.page.page import Page
from papersize import SIZES, parse_length

from iso639 import Lang


class Project:
    version = 3

    def __init__(self, name, description):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.pages: List[Page] = []
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

    def export(self):
        export_path = self.settings.get("export_path")
        export_scaling_factor = self.settings.get("export_scaling_factor")

        for page in self.pages:
            exporter = ExporterHTML(export_path, f"{page.order}.html")
            exporter.scaling_factor = export_scaling_factor
            exporter.export(page.generate_export_data())

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

        for page_data in project_data["pages"]:
            page = Page.from_dict(page_data, project.settings)
            project.add_page(page)

        project.settings = ProjectSettings.from_dict(project_data["settings"])

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
