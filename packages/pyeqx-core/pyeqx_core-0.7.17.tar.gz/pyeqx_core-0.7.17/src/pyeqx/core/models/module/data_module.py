from dataclasses import dataclass
from typing import Optional, Type, TypeVar, cast

from pyeqx.core.common import to_dict
from pyeqx.core.enums import DataModuleType
from pyeqx.core.models.module.properties import (
    DataModuleProperties,
    FileDataModuleProperties,
    DatabaseDataModuleProperties,
    ApiDataModuleProperties,
    StreamDataModuleProperties,
)

T = TypeVar("T", bound=DataModuleProperties)


@dataclass
class DataModule:
    type: DataModuleType
    properties: DataModuleProperties

    def get_properties(self, cls: Optional[Type[T]] = None) -> T:
        props = self.properties

        if cls is None:
            return props

        if self.type == DataModuleType.File:
            props = FileDataModuleProperties.from_properties(self.properties)
        elif self.type == DataModuleType.Database:
            props = DatabaseDataModuleProperties.from_properties(self.properties)
        elif self.type == DataModuleType.Api:
            props = ApiDataModuleProperties.from_properties(self.properties)
        elif self.type == DataModuleType.Stream:
            props = StreamDataModuleProperties.from_properties(self.properties)

        if isinstance(props, cls):
            return cast(T, props)

        return props

    @staticmethod
    def from_dict(obj: any) -> "DataModule":
        assert isinstance(obj, dict)
        parse_type = DataModuleType(obj.get("type"))

        if parse_type == DataModuleType.File:
            parse_properties = FileDataModuleProperties.from_dict(obj.get("properties"))
        elif parse_type == DataModuleType.Database:
            parse_properties = DatabaseDataModuleProperties.from_dict(
                obj.get("properties")
            )
        elif parse_type == DataModuleType.Api:
            parse_properties = ApiDataModuleProperties.from_dict(obj.get("properties"))
        elif parse_type == DataModuleType.Stream:
            parse_properties = StreamDataModuleProperties.from_dict(
                obj.get("properties")
            )
        else:
            parse_properties = obj.get("properties")

        return DataModule(parse_type, parse_properties)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = self.type
        result["properties"] = to_dict(DataModuleProperties, self.properties)
