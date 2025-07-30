from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_str
from pyeqx.core.models.storage.properties.sql_data_properties import (
    SqlDataProperties,
)


@dataclass
class MSSqlDataProperties(SqlDataProperties):
    def __init__(self, url, db):
        super().__init__(url, db)

    @staticmethod
    def from_dict(obj: Any) -> "MSSqlDataProperties":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        db = from_str(obj.get("db"))
        return MSSqlDataProperties(url, db)

    def from_properties(self) -> "MSSqlDataProperties":
        return MSSqlDataProperties(self.url, self.db)
