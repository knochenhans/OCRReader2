import json
import os
from typing import Any, Dict, Optional
from loguru import logger


class Settings:
    def __init__(
        self, name: str = "", path: str = "", default_path: str = "src/data/"
    ) -> None:
        self.settings: Dict[str, Any] = {}
        self.name = name
        self.path = path

        self.default_path = default_path
        self.file_path = os.path.join(self.path, f"{self.name}.json")
        self.default_file_path = os.path.join(
            self.default_path, f"default_{self.name}.json"
        )

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.settings.get(key, default)

    def load(self) -> None:
        self.settings = {}

        # Load default settings and override with user settings
        if os.path.exists(self.default_file_path):
            with open(self.default_file_path, "r") as f:
                self.settings.update(json.load(f))

        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.settings.update(json.load(f))

    def save(self) -> None:
        file_path = os.path.join(self.path, f"{self.name}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def to_dict(self) -> Dict[str, Any]:
        return self.settings

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        settings = cls(data.get("name", ""), data.get("path", ""))
        settings.settings = data.get("settings", {})
        return settings

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Settings):
            return False
        return self.settings == other.settings
