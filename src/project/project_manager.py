import json
import os
from typing import Optional, List, Tuple

from loguru import logger
from project.project import Project  # type: ignore
from project.project_settings import ProjectSettings  # type: ignore


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
        project_dict = project.to_dict()

        file_path = os.path.join(
            self.project_folder, project.uuid, f"{project.uuid}.json"
        )

        with open(file_path, "w") as f:
            json.dump(project_dict, f)
        logger.info(f"Finished saving project: {file_path}")

        # Save metadata.json
        metadata = {"name": project.name}
        metadata_file_path = os.path.join(
            self.project_folder, project.uuid, "metadata.json"
        )

        with open(metadata_file_path, "w") as f:
            json.dump(metadata, f)
        logger.info(f"Finished saving metadata: {metadata_file_path}")

    def new_project(self, name: str, description: str = "") -> Project:
        project = Project(name, description)

        project_settings_json = {}

        try:
            with open("src/main_window/default_project_settings.json", "r") as f:
                project_settings_json = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load default project settings: {e}")

        project_settings = ProjectSettings(project_settings_json)
        project.settings = project_settings

        self.add_project(project)
        self.save_project_(project)
        return project

    def load_project(self, uuid: str) -> Project:
        file_path = os.path.join(self.project_folder, uuid, f"{uuid}.json")
        with open(file_path, "r") as f:
            loaded_data = json.load(f)
        return Project.from_dict(loaded_data)
