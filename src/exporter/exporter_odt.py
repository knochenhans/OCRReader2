from typing import Dict, Any
from odf.opendocument import OpenDocumentText, OpenDocument # type: ignore
from odf.text import P # type: ignore
from odf.draw import Frame, TextBox # type: ignore
from loguru import logger

from exporter.exporter import Exporter


class ExporterODT(Exporter):
    def export_page(self, export_data: Dict[str, Any]) -> None:
        try:
            doc = OpenDocumentText()

            paper_size = export_data["page"].get("paper_size", "A4")

            # Set paper size for the document
            if paper_size == "A4":
                doc.text.setAutomaticStyles(
                    {"page-size": "21cm 29.7cm", "margin": "0cm"}
                )
            elif paper_size == "Letter":
                doc.text.setAutomaticStyles(
                    {"page-size": "21.59cm 27.94cm", "margin": "2.54cm"}
                )

            ppi = export_data["page"].get("ppi", 300)

            for export_data_entry in export_data["boxes"]:
                if export_data_entry["type"] == "text":
                    logger.info(
                        f"Exporting text of box {export_data_entry['id']}: {export_data_entry['text']}"
                    )

                    if "position" in export_data_entry:
                        x = self.pixel_to_cm(export_data_entry["position"]["x"], ppi)
                        y = self.pixel_to_cm(export_data_entry["position"]["y"], ppi)
                        width = self.pixel_to_cm(
                            export_data_entry["position"]["width"], ppi
                        )
                        height = self.pixel_to_cm(
                            export_data_entry["position"]["height"], ppi
                        )

                        self._create_text_frame(
                            doc,
                            export_data_entry,
                            name=f"Textbox_{export_data_entry['id']}",
                            x=x,
                            y=y,
                            width=width,
                            height=height,
                        )

            doc.save(self.output_path + ".odt")
        except Exception as e:
            logger.error(f"Failed to export to ODT: {e}")

    def _create_text_frame(
        self,
        doc: OpenDocument,
        export_data_entry: Dict[str, Any],
        name: str = "Textbox",
        x: float = 0,
        y: float = 0,
        width: float = 0,
        height: float = 0,
    ) -> None:
        text = export_data_entry["text"]
        name = export_data_entry.get("name", "Textbox")
        frame = Frame(
            width=f"{width}cm", height=f"{height}cm", name=name, x=f"{x}cm", y=f"{y}cm"
        )
        textbox = TextBox()
        paragraph = P(text=text)
        textbox.addElement(paragraph)
        frame.addElement(textbox)
        doc.text.addElement(frame)
