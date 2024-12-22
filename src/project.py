from typing import List, Optional

from loguru import logger
from src.exporter.exporter_html import ExporterHTML
from src.page.page import Page


class Project:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.langs = []
        self.pages: List[Page] = []
        self.project_path = ""
        self.output_path = ""
        self.scaling_factor = 1.2

    def add_image(self, image_path: str):
        logger.info(f"Adding image: {image_path}")
        self.add_page(Page(image_path, langs=self.langs))

    def add_images(self, image_paths: List[str]):
        for image_path in image_paths:
            self.add_image(image_path)

    # def add_pdf(self, pdf_path: str):
    #     logger.info(f"Adding PDF: {pdf_path}")
        
    #     # Extract images from PDF
    #     images = self.extract_images_from_pdf(pdf_path)
    #     self.add_images(images)

    # def extract_images_from_pdf(self, pdf_path: str) -> List[str]:
    #     from PyPDF2 import PdfFileReader
    #     import fitz

    #     images = []

    #     with open(pdf_path, "rb") as f:
    #         pdf = PdfFileReader(f)
    #         for page_num in range(pdf.getNumPages()):
    #             page = pdf.getPage(page_num)
    #             images.extend(self.extract_images_from_pdf_page(page))

    def add_page(self, page: Page, index: Optional[int] = None):
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

    def export(self):
        for page in self.pages:
            exporter = ExporterHTML(self.output_path, f"{page.order}.html")
            exporter.scaling_factor = self.scaling_factor
            exporter.export(page.generate_export_data())

    def to_dict(self) -> dict:
        return {
            "project": {
                "name": self.name,
                "description": self.description,
                "langs": self.langs,
                "pages": [page.to_dict() for page in self.pages],
                "output_path": self.output_path,
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        project_data = data["project"]

        project = cls(project_data["name"], project_data["description"])
        project.langs = project_data["langs"]
        project.output_path = project_data["output_path"]

        for page_data in project_data["pages"]:
            page = Page.from_dict(page_data)
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
        return f"Project(name={self.name}, description={self.description}, pages={self.pages})"

    def __repr__(self) -> str:
        return self.__str__()
