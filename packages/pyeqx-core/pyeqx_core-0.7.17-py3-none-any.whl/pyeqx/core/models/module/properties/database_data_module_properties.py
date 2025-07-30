from dataclasses import dataclass
from typing import Any
from pyeqx.core.common import from_str
from pyeqx.core.models.module.properties.data_module_properties import (
    DataModuleProperties,
)


@dataclass
class DatabaseDataModuleProperties(DataModuleProperties):
    table: str

    def __init__(self, storage: str, table: str):
        parsed_obj = {
            "table": table,
        }
        super().__init__(storage, parsed_obj)

    @staticmethod
    def from_dict(obj: Any) -> "DatabaseDataModuleProperties":
        assert isinstance(obj, dict)
        storage = from_str(obj.get("storage"))
        table = from_str(obj.get("table"))
        return DatabaseDataModuleProperties(storage, table)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({"table": self.table})
        return result

    def from_properties(self) -> "DatabaseDataModuleProperties":
        return DatabaseDataModuleProperties(self.storage, self.table)
