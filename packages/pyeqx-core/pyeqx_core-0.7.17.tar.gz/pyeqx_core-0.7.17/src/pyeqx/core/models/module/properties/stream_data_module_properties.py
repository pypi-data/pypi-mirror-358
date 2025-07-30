from dataclasses import dataclass

from pyeqx.core.common import from_dict, from_str
from pyeqx.core.models.module.properties.data_module_properties import (
    DataModuleProperties,
)


@dataclass
class StreamDataModuleProperties(DataModuleProperties):
    name: str
    options: dict

    def __init__(self, storage: str, name: str, options: dict):
        parsed_obj = {
            "name": name,
            "options": options,
        }
        super().__init__(storage, parsed_obj)

    @staticmethod
    def from_dict(obj: dict) -> "StreamDataModuleProperties":
        assert isinstance(obj, dict)
        storage = from_str(obj.get("storage"))
        name = from_str(obj.get("name"))

        # optional for options
        options = from_dict(obj.get("options")) if "options" in obj else {}

        return StreamDataModuleProperties(storage=storage, name=name, options=options)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({"name": self.name, "options": self.options})
        return result

    def from_properties(self) -> "StreamDataModuleProperties":
        return StreamDataModuleProperties(
            storage=self.storage, name=self.name, options=self.options
        )
