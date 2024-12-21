from typing import Dict
from abc import ABC, abstractmethod


class Exporter(ABC):
    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    @abstractmethod
    def export(self, export_data: Dict) -> None:
        pass

    def pixel_to_cm(self, pixels: int, ppi: int) -> float:
        return pixels / ppi * 2.54
