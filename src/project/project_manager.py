import json
import os
from typing import Optional

from loguru import logger
from project.project import Project # type: ignore


class ProjectManager:
    def __init__(self, project_folder: str):
        self.projects: list[Project] = []
        self.current_project = None
        self.project_folder = project_folder

        projects = os.listdir(project_folder)

        logger.info(f"Founds projects: {len(projects)}")
        logger.info(f"Loading projects from: {project_folder}")

        # Try to load all projects from the project folder
        for folder in projects:
            logger.info(f"Loading project: {folder}")
            uuid = folder
            file_path = os.path.join(project_folder, folder, f"{uuid}.json")

            if os.path.exists(file_path):
                self.import_project(file_path)
                logger.info(f"Loaded project: {file_path}")
            else:
                logger.error(
                    f"Empty project folder found: {file_path}, removing folder"
                )
                os.rmdir(os.path.join(project_folder, folder))

    def add_project(self, project: Project):
        self.projects.append(project)

        project_root_path = os.path.join(self.project_folder, project.uuid)

        if not os.path.exists(project_root_path):
            os.makedirs(project_root_path)
        project.project_folder = project_root_path

    def remove_project(self, index: int):
        # Delete project folder
        project = self.projects.pop(index)

        project_root_path = os.path.join(self.project_folder, project.uuid)

        if os.path.exists(project_root_path):
            os.rmdir(project_root_path)

    def get_project(self, index: int) -> Project:
        return self.projects[index]

    def get_project_by_uuid(self, uuid: str) -> Optional[Project]:
        for project in self.projects:
            if project.uuid == uuid:
                return project
        return None

    def get_project_count(self) -> int:
        return len(self.projects)

    def import_project(self, file_path: str) -> None:
        try:
            logger.info(f"Importing project: {file_path}")
            with open(file_path, "r") as f:
                loaded_data = json.load(f)

            project = Project.from_dict(loaded_data)

            logger.info(f"Project pages: {project.get_page_count()}")

            self.add_project(project)
        except Exception as e:
            raise Exception(f"Failed to import project: {e}")

    def save_project(self, index: int) -> None:
        logger.info(f"Saving project: {index}")
        project = self.get_project(index)
        project_dict = project.to_dict()

        file_path = os.path.join(
            self.project_folder, project.uuid, f"{project.uuid}.json"
        )

        with open(file_path, "w") as f:
            json.dump(project_dict, f)
        logger.info(f"Finsihed saving project: {file_path}")

    def new_project(self, name: str, description: str) -> Project:
        project = Project(name, description)
        self.add_project(project)
        return project
