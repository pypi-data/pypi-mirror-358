from dataclasses import dataclass
from typing import Any
from pyeqx.core.common import from_dict, from_str
from pyeqx.core.models.module.properties.data_module_properties import (
    DataModuleProperties,
)


@dataclass
class FileDataModuleProperties(DataModuleProperties):
    type: str
    path: str
    options: dict

    def __init__(self, storage: str, type: str, path: str, options: dict):
        parsed_obj = {
            "type": type,
            "path": path,
            "options": options,
        }
        super().__init__(storage, parsed_obj)

    @staticmethod
    def from_dict(obj: Any) -> "FileDataModuleProperties":
        assert isinstance(obj, dict)
        storage = from_str(obj.get("storage"))
        type = from_str(obj.get("type"))
        path = from_str(obj.get("path"))

        # optional for options
        options = from_dict(obj.get("options")) if "options" in obj else {}

        return FileDataModuleProperties(
            storage=storage, type=type, path=path, options=options
        )

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({"type": self.type, "path": self.path, "options": self.options})
        return result

    def from_properties(self) -> "FileDataModuleProperties":
        return FileDataModuleProperties(
            storage=self.storage, type=self.type, path=self.path, options=self.options
        )
