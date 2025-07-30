from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_str
from pyeqx.core.models.storage.properties.data_properties import DataProperties


@dataclass
class CassandraDataProperties(DataProperties):
    keyspace: str

    def __init__(self, keyspace):
        parsed_obj: dict = {}
        parsed_obj["keyspace"] = keyspace
        self.__dict__ = parsed_obj

    @staticmethod
    def from_dict(obj: Any) -> "CassandraDataProperties":
        assert isinstance(obj, dict)
        keyspace = from_str(obj.get("keyspace"))
        return CassandraDataProperties(keyspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["keyspace"] = from_str(self.keyspace)
        return result

    def from_properties(self) -> "CassandraDataProperties":
        return CassandraDataProperties(self.keyspace)
