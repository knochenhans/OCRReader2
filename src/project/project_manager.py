import json
import os
from typing import Optional, List, Tuple

from loguru import logger
from project.project import Project  # type: ignore
from settings import Settings  # type: ignore
from page.page import Page  # type: ignore
from ocr_processor import OCRProcessor  # type: ignore


class ProjectManager:
    def __init__(self, project_folder: str):
        self.projects: List[Tuple[str, str]] = []
        self.current_project: Optional[Project] = None
        self.project_folder = project_folder

        # Ensure the project folder exists
        if not os.path.exists(project_folder):
            logger.info(f"Project folder not found, creating: {project_folder}")
            os.makedirs(project_folder)

        projects = os.listdir(project_folder)

        logger.info(f"Found projects: {len(projects)}")
        logger.info(f"Loading projects from: {project_folder}")

        # Try to load all projects from the project folder
        for folder in projects:
            logger.info(f"Loading project: {folder}")
            uuid = folder
            metadata_file_path = os.path.join(project_folder, folder, "metadata.json")

            if os.path.exists(metadata_file_path):
                with open(metadata_file_path, "r") as f:
                    metadata = json.load(f)
                self.projects.append((metadata["name"], uuid))
                logger.info(f"Loaded project metadata: {metadata_file_path}")
            else:
                logger.error(
                    f"Empty project folder found: {metadata_file_path}, removing folder"
                )
                os.rmdir(os.path.join(project_folder, folder))

    def add_project(self, project: Project):
        self.projects.append((project.name, project.uuid))

        project_root_path = os.path.join(self.project_folder, project.uuid)

        if not os.path.exists(project_root_path):
            os.makedirs(project_root_path)
        project.folder = project_root_path

    def remove_project(self, index: int):
        project_name, project_uuid = self.projects.pop(index)

        project_root_path = os.path.join(self.project_folder, project_uuid)

        if os.path.exists(project_root_path):
            os.rmdir(project_root_path)

    def get_project(self, index: int) -> Project:
        project_name, project_uuid = self.projects[index]
        return self.load_project(project_uuid)

    def get_project_by_uuid(self, uuid: str) -> Optional[Project]:
        for name, project_uuid in self.projects:
            if project_uuid == uuid:
                return self.load_project(project_uuid)
        return None

    def get_project_count(self) -> int:
        return len(self.projects)

    def import_project(self, file_path: str) -> str:
        try:
            logger.info(f"Importing project: {file_path}")
            with open(file_path, "r") as f:
                loaded_data = json.load(f)

            project = Project.from_dict(loaded_data)

            logger.info(f"Project pages: {project.get_page_count()}")

            self.add_project(project)
        except Exception as e:
            raise Exception(f"Failed to import project: {e}")

        return project.uuid

    def save_current_project(self) -> None:
        if self.current_project:
            self.save_project_(self.current_project)

    def save_project(self, index: int) -> None:
        project = self.get_project(index)
        self.save_project_(project)

    def save_project_(self, project: Project) -> None:
        logger.info(f"Saving project: {project.uuid}")

        self.save_project_pages(project)

        project_file_path = os.path.join(
            self.project_folder, project.uuid, "project.json"
        )
        project_dict = project.to_dict()

        with open(project_file_path, "w") as f:
            json.dump(project_dict, f)
        logger.info(f"Finished saving project: {project_file_path}")

        self.save_metadata(project)

    def load_project(self, uuid: str) -> Project:
        project_file_path = os.path.join(self.project_folder, uuid, "project.json")

        if not os.path.exists(project_file_path):
            raise FileNotFoundError(f"Project file not found: {project_file_path}")

        with open(project_file_path, "r") as f:
            loaded_data = json.load(f)
        project = Project.from_dict(loaded_data)
        project.folder = os.path.join(self.project_folder, uuid)

        self.load_project_pages(project)
        self.load_metadata(project)

        return project

    def save_metadata(self, project: Project) -> None:
        metadata = {"name": project.name}
        metadata_file_path = os.path.join(
            self.project_folder, project.uuid, "metadata.json"
        )

        with open(metadata_file_path, "w") as f:
            json.dump(metadata, f)
        logger.info(f"Finished saving metadata: {metadata_file_path}")

    def load_metadata(self, project: Project) -> None:
        metadata_file_path = os.path.join(
            self.project_folder, project.uuid, "metadata.json"
        )

        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, "r") as f:
                metadata = json.load(f)
            project.name = metadata["name"]

    def save_project_pages(self, project: Project) -> None:
        pages_folder = os.path.join(self.project_folder, project.uuid, "pages")

        if not os.path.exists(pages_folder):
            os.makedirs(pages_folder)

        # Remove all existing page files
        for file in os.listdir(pages_folder):
            if file.endswith(".json"):
                os.remove(os.path.join(pages_folder, file))

        for page in project.pages:
            page_dict = page.to_dict()
            page_file_path = os.path.join(pages_folder, f"{page.order}.json")
            with open(page_file_path, "w") as f:
                json.dump(page_dict, f)

        logger.info(f"Finished saving project pages: {pages_folder}")

    def load_project_pages(self, project: Project) -> None:
        pages_folder = os.path.join(self.project_folder, project.uuid, "pages")

        if not os.path.exists(pages_folder):
            return

        page_files = [
            file for file in os.listdir(pages_folder) if file.endswith(".json")
        ]
        page_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

        for file in page_files:
            with open(os.path.join(pages_folder, file), "r") as f:
                page_dict = json.load(f)
            project.add_page(Page.from_dict(page_dict))
        project.set_ocr_processor(OCRProcessor(project.settings))

        logger.info(f"Finished loading project pages: {pages_folder}")

    def new_project(self, name: str, description: str = "") -> Project:
        project = Project(name, description)

        project_settings_json = {}

        try:
            with open("src/main_window/default_project_settings.json", "r") as f:
                project_settings_json = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load default project settings: {e}")

        project_settings = Settings(project_settings_json)
        project.settings = project_settings

        self.add_project(project)
        self.save_project_(project)
        return project

    def close_current_project(self) -> None:
        self.current_project = None
