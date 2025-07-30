from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_str
from pyeqx.core.models.storage.properties.data_properties import DataProperties


@dataclass
class SqlDataProperties(DataProperties):
    url: str
    db: str

    def __init__(self, url, db):
        parsed_obj = {
            "url": url,
            "db": db,
        }
        super().__init__(parsed_obj)

    @staticmethod
    def from_dict(obj: Any) -> "SqlDataProperties":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        db = from_str(obj.get("db"))
        return SqlDataProperties(url, db)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        result["db"] = from_str(self.db)
        return result

    def from_properties(self) -> "SqlDataProperties":
        return SqlDataProperties(self.url, self.db)
