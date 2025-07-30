from dataclasses import dataclass
from typing import Any


@dataclass
class DataModuleProperties(dict):
    storage: str

    def __init__(self, storage: str, obj: dict[str, Any]):
        obj.update({"storage": storage})

        self.__dict__ = obj

    def to_dict(self) -> dict:
        result = {
            "storage": self.storage,
        }
        return result
