import json
import os
from typing import Any, Dict, Optional


class ProjectSettings:
    def __init__(self, default_settings: Optional[Dict[str, Any]] = None) -> None:
        self.settings: Dict[str, Any] = default_settings or {}

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.settings.get(key, default)

    def load(self, file_path: str) -> None:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.settings = json.load(f)
        else:
            raise FileNotFoundError(f"Settings file not found: {file_path}")

    def save(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def to_dict(self) -> Dict[str, Any]:
        return self.settings

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSettings":
        return cls(data)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProjectSettings):
            return False
        return self.settings == other.settings
