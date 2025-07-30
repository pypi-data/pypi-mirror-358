from dataclasses import dataclass
from typing import Any
from pyeqx.core.common import from_dict, from_str
from pyeqx.core.models.module.properties.data_module_properties import (
    DataModuleProperties,
)


@dataclass
class ApiDataModuleProperties(DataModuleProperties):
    path: str
    method: str
    parameters: dict
    body: dict

    def __init__(
        self, storage: str, path: str, method: str, parameters: dict, body: dict
    ):
        parsed_obj = {
            "path": path,
            "method": method,
            "parameters": parameters,
            "body": body,
        }
        super().__init__(storage, parsed_obj)

    @staticmethod
    def from_dict(obj: Any) -> "ApiDataModuleProperties":
        assert isinstance(obj, dict)
        storage = from_str(obj.get("storage"))
        path = from_str(obj.get("path"))
        method = str.lower(from_str(obj.get("method")))
        parameters = from_dict(obj.get("parameters"))

        # optional for POST method
        body = from_dict(obj.get("body")) if "body" in obj else {}

        return ApiDataModuleProperties(
            storage=storage, path=path, method=method, parameters=parameters, body=body
        )

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update(
            {
                "path": self.path,
                "method": self.method,
                "parameters": self.parameters,
                "body": self.body,
            }
        )
        return result

    def from_properties(self) -> "ApiDataModuleProperties":
        return ApiDataModuleProperties(
            storage=self.storage,
            path=self.path,
            method=self.method,
            parameters=self.parameters,
            body=self.body,
        )
