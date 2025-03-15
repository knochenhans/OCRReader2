import pytest
from settings import Settings  # type: ignore
from src.ocr_engine.ocr_result import OCRResultBlock
from src.ocr_processor import OCRProcessor
from src.page.ocr_box import OCRBox, TextBox
from src.page.page import Page
from src.ocr_engine.ocr_result_writer import OCRResultWriter


class UnhyphenationHelper:
    def __init__(self, page: Page) -> None:
        self.page = page

    def unhyphenate(self) -> None:
        pass


@pytest.fixture
def project_settings():
    return Settings.from_dict(
        {
            "settings": {
                "ppi": 300,
                "langs": ["deu"],
                "paper_size": "a4",
                "export_scaling_factor": 1.2,
                "export_path": "",
            }
        }
    )


@pytest.fixture
def application_settings():
    return Settings.from_dict(
        {
            "settings": {
                "is_maximized": True,
                "custom_shortcuts": {
                    "Ctrl + 1": "section",
                    "Alt + 1": "FLOWING_TEXT",
                    "Alt + 2": "HEADING_TEXT",
                    "Alt + 3": "PULLOUT_TEXT",
                },
                "tesseract_options": "preserve_interword_spaces=1",
                "thumbnail_size": 150,
                "merged_word_in_dict_color": 4278802740,
                "merged_word_not_in_dict_color": 4289010989,
                "editor_background_color": 4294966227,
                "max_font_size": 0,
                "min_font_size": 0,
                "round_font_size": 1,
                "scale_factor": 1.2,
                "box_flow_line_color": 4278190080,
                "box_type_tags": {
                    "UNKNOWN": "",
                    "FLOWING_TEXT": "p",
                    "HEADING_TEXT": "h2",
                    "PULLOUT_TEXT": "h3",
                    "VERTICAL_TEXT": "p",
                    "CAPTION_TEXT": "p",
                    "EQUATION": "",
                    "INLINE_EQUATION": "",
                    "TABLE": "",
                    "FLOWING_IMAGE": "",
                    "HEADING_IMAGE": "",
                    "PULLOUT_IMAGE": "",
                    "HORZ_LINE": "",
                    "VERT_LINE": "",
                    "NOISE": "",
                    "COUNT": "",
                },
                "confidence_color_threshold": 85,
                "box_flow_line_alpha": 128,
                "box_item_symbol_size": 16,
                "html_export_section_class": "section",
                "editor_text_color": 4278190080,
                "box_item_order_font_color": 4289010989,
                "box_item_symbol_font_color": 4289010989,
            }
        }
    )


@pytest.fixture
def image_path():
    return "data/1.jpeg"


@pytest.fixture
def page(project_settings, image_path):
    page = Page(image_path, ocr_processor=OCRProcessor(project_settings))
    page.set_project_settings(project_settings)
    page.analyze_page()
    page.recognize_ocr_boxes()
    return page


def test1_test(page, application_settings) -> None:
    box: OCRBox = page.layout[2]

    assert box.get_text() == "EDITORIAL"  # type: ignore

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    # if isinstance(box.ocr_results, OCRResultBlock):
    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert document.toPlainText() == box.get_text()  # type: ignore


def test2_test(page, application_settings) -> None:
    box: OCRBox = page.layout[7]

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert (
        document.toPlainText()
        == "Drei erstklassige Rennpferde hat Commodore mit den Amigas im Stall. Der Amiga 500 wird für frischen Wind in der gehobenen Heimcompu- terszene sorgen. Mit eingebautem Laufwerk, deutscher Tastatur und fantastischen Gra- fikeigenschaften eignet er sich geradezu ideal, um als Ein- und Umsteigermodell ein Ren-"
    )
