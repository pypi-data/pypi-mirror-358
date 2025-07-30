from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_str
from pyeqx.core.models.storage.properties.sql_data_properties import (
    SqlDataProperties,
)


@dataclass
class PostgreSqlDataProperties(SqlDataProperties):
    @staticmethod
    def from_dict(obj: Any) -> "PostgreSqlDataProperties":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        db = from_str(obj.get("db"))
        return PostgreSqlDataProperties(url, db)

    def from_properties(self) -> "PostgreSqlDataProperties":
        return PostgreSqlDataProperties(self.url, self.db)
