import os
from settings.settings import Settings  # type: ignore
from src.ocr_processor import OCRProcessor
from src.project.project_manager import ProjectManager  # type: ignore

project_settings = Settings.from_dict(
    {
        "ppi": 300,
        "langs": ["deu"],
        "paper_size": "a4",
        "export_scaling_factor": 1.2,
        "export_path": "",
    }
)
image_path = "data/1.jpeg"


def test_project_manager1():
    os.system("rm -rf /tmp/ocrreader/tests")

    project_manager = ProjectManager("/tmp/ocrreader/tests")

    assert len(project_manager.projects) == 0


def test_project_manager2():
    os.system("rm -rf /tmp/ocrreader/tests")

    project_manager = ProjectManager("/tmp/ocrreader/tests")

    project1 = project_manager.new_project("Test", "Test", "data/")

    assert len(project_manager.projects) == 1
    assert project1.name == "Test"
    assert project1.description == "Test"
    assert project1.settings.get("ppi") == 300  # type: ignore

    project2 = project_manager.new_project("Test2", "Test2", "data/")

    assert len(project_manager.projects) == 2
    assert project2.name == "Test2"
    assert project2.description == "Test2"
    assert project2.settings.get("ppi") == 300  # type: ignore

    project_manager.remove_project_by_uuid(project1.uuid)

    assert len(project_manager.projects) == 1

    project2 = project_manager.load_project(project2.uuid)

    assert project2.name == "Test2"
    assert project2.description == "Test2"
    assert project2.settings.get("ppi") == 300  # type: ignore


def test_project_manager3():
    os.system("rm -rf /tmp/ocrreader/tests")

    project_manager = ProjectManager("/tmp/ocrreader/tests")

    project1 = project_manager.new_project("Test", "Test", "data/")

    uuid = project1.uuid

    project_manager.current_project = project1

    image_path = "data/1.jpeg"

    project1.add_image(image_path)
    project1.set_ocr_processor(OCRProcessor(project_settings))
    project1.analyze_pages()
    project1.recognize_page_boxes()

    project_manager.save_current_project()
    project_manager.close_current_project()

    project1 = None
    project_manager = None

    project_manager = ProjectManager("/tmp/ocrreader/tests")
    project1 = project_manager.load_project(uuid)

    assert project1.name == "Test"
    assert project1.description == "Test"
    assert project1.settings.get("ppi") == 300  # type: ignore
    assert len(project1.pages) == 1
    assert os.path.abspath(project1.pages[0].image_path) == os.path.abspath(image_path)  # type: ignore
