import pytest

from src.ocr_engine.ocr_result_writer import OCRResultWriter  # type: ignore
from src.ocr_processor import OCRProcessor
from src.page.ocr_box import OCRBox
from src.page.page import Page
from src.settings.settings import Settings  # type: ignore


class UnhyphenationHelper:
    def __init__(self, page: Page) -> None:
        self.page = page

    def unhyphenate(self) -> None:
        pass


@pytest.fixture
def project_settings():
    return Settings.from_dict(
        {
            "ppi": 200,
            "langs": ["deu"],
            "paper_size": "a4",
            "export_scaling_factor": 1.2,
            "export_path": "",
            "tesseract_data_path": "/usr/share/tessdata",
            "layout_analyzer": "tesserocr",
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
def image_path1():
    return "data/1.jpeg"


@pytest.fixture
def image_path2():
    return "data/4.jpeg"


@pytest.fixture
def image_path3():
    return "data/5.jpeg"


@pytest.fixture
def page1(project_settings, image_path1):
    page = Page(image_path1, ocr_processor=OCRProcessor(project_settings))
    page.analyze_page(project_settings)
    page.recognize_ocr_boxes()
    return page


@pytest.fixture
def page2(project_settings, image_path2):
    page = Page(image_path2, ocr_processor=OCRProcessor(project_settings))
    page.analyze_page(project_settings)
    page.recognize_ocr_boxes()
    return page


def test_ocr_results1(page1, application_settings) -> None:
    box: OCRBox = page1.layout[3]

    assert box.get_text() == "EDITORIAL"  # type: ignore

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    # if isinstance(box.ocr_results, OCRResultBlock):
    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert document.toPlainText() == box.get_text()  # typ1e: ignore


def test_ocr_results2(page1, application_settings) -> None:
    box: OCRBox = page1.layout[5]

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert (
        document.toPlainText()
        == "Drei erstklassige Rennpferde hat Commodore mit den Amigas im Stall. Der Amiga 500 wird für frischen Wind in der gehobenen Heimcomputerszene sorgen. Mit eingebautem Laufwerk, deutscher Tastatur und fantastischen Grafikeigenschaften eignet er sich geradezu ideal, um als Ein- und Umsteigermodell ein Ren-"
    )


# def test_ocr_results3(application_settings) -> None:
#     text_parts = []
#     text_parts.append(TextPart(TextPartType.TEXT, "Dies ist ein ", "", ""))
#     text_parts.append(TextPart(TextPartType.HYPHENATED_WORD, "Test", "Test-", "wort"))

#     ocr_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

#     assert (
#         ocr_writer._text_parts_to_qdocument(text_parts).toPlainText()
#         == "Dies ist ein Testwort"
#     )


def test_ocr_results4(image_path2, application_settings, project_settings) -> None:
    page = Page(image_path2, ocr_processor=OCRProcessor(project_settings))
    page.analyze_page(project_settings)
    page.recognize_ocr_boxes()

    box: OCRBox = page.layout[2]

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    if box.ocr_results is None:
        return

    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert (
        document.toPlainText()
        == """programmiert. Ebenso wird mit dem Timer verfahren, wobei das Argument (hier eins) angibt, in welchem Sekundenintervall dieser Aufruf durchgeführt werden soll. Dann soll ein Kreis mit dem Radius.r und dem Mittelpunkt (xpos,ypos) gezeichnet werden. Falls Sie sich über die etwas seltsame WHILE...WEND-Schleifenkonstruktion wundern: Hinter dem WHILE-Befehl steht normalerweise eine logische Bedingung wie etwa »x < 100« und die WHILE-Schleife wird so lange ausgeführt, bis diese Bedingung unwahr ist. Nun ist es aber eine Eigenschaft von Basic, allen von Null verschiedenen Zahlen den logischen Wert »wahr« zuzuordnen, während die Zahl Null logisch »falsch« entspricht. Damit ist der Wert eins gleichbedeutend mit »wahr« und so haben wir eine Endlosschleife konstruiert.\nWäre Ihr Amiga ein Heimcomputer ohne die Fähigkeiten des Multitasking, wäre der im Schleifenkörper enthaltene Befehl SLEEP sinnlos, da sich Basic im Moment sowieso in einer Endlosschleife befindet. Der SLEEP-Befehl führt jedoch dazu, daß Ihr Basic-Programm solange angehalten wird, bis ein Unterbrechungsereignis eintritt. Gegenüber der normalen Endlosschleife hat dies den Vorteil, daß Ihr Programm anderen, gleichzeitig laufenden Programmen mehr Laufzeit zur Verfügung stellt. Das Basicprogramm wartet in diesem Zustand also nur darauf, daß Sie die Maustaste bedienen. (In der heutigen Zeit bringen wohl nur noch Computer hierfür die Geduld auf.)\nWelche Funktion. hat das Programm nun? In der ersten Zeile nach dem Label »Maus:« wird der augenblickliche Zustand der Maustaste überprüft. Das Programm unterscheidet zwei Zustände. Erstens: die Maustaste wurde ein-, zwei- oder dreimal kurz betätigt. Zweitens: die Maustaste bleibt längere Zeit gedrückt. Da Ihr Amiga sehr eilfertig ist, werden Sie keine Zeit haben, den Finger von der Maus zu nehmen. Schon wird angezeigt, daß die Auswahltaste gegenwärtig gedrückt ist. Um Ihnen die Zeit zu"""
    )


def test_ocr_results5(image_path3, application_settings, project_settings) -> None:
    page = Page(image_path3, ocr_processor=OCRProcessor(project_settings))
    page.analyze_page(project_settings)
    page.recognize_ocr_boxes()

    box: OCRBox = page.layout[67]

    ocr_result_writer = OCRResultWriter(application_settings, "de", ["und", "oder"])

    if box.ocr_results is None:
        return

    document = ocr_result_writer.to_qdocument([box.ocr_results])  # type: ignore

    assert (
        document.toPlainText()
        == """Neu in diesem Programm ist nur der sizeof-Operator in Zeile 170 und 180. sizeof liefert die Größe seines in Klammern folgenden Operanden in Bytes. Dieser Wert wird, mit Hilfe der Formatanweisung »%d«, in den Ausgabetext eingefügt.\nZeichenvariablen (Character-Variablen) können die Werte von Zeichen aufnehmen."""
    )
