from typing import Any, Dict, Optional

from settings import Settings # type: ignore


class PageSettings:
    def __init__(self, project_settings: Settings) -> None:
        self.page_settings: Dict[str, Any] = {}
        self.project_settings: Settings = project_settings

    def set(self, key: str, value: Any) -> None:
        self.page_settings[key] = value

    def get(self, key: str) -> Optional[Any]:
        if key in self.page_settings:
            return self.page_settings[key]
        elif self.project_settings:
            return self.project_settings.get(key)
        return None

    def to_dict(self) -> Dict[str, Any]:
        return self.page_settings

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], project_settings: Settings
    ) -> "PageSettings":
        page_settings = cls(project_settings)
        page_settings.page_settings = data
        return page_settings

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PageSettings):
            return False
        return self.page_settings == other.page_settings
