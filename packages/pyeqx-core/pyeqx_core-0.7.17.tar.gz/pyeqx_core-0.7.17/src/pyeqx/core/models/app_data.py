from typing import Any

from pyeqx.core.enums import DataModuleType
from pyeqx.core.models.app_data_base import AppDataBase
from pyeqx.core.models.module import DataModule


class AppData(AppDataBase):
    src: DataModule
    dest: DataModule

    def __init__(self):
        self.src = DataModule(DataModuleType.Default, {})
        self.dest = DataModule(DataModuleType.Default, {})

    def parse(self, obj: Any):
        assert isinstance(obj, dict)

        raw_src = obj.get("src")

        if raw_src is not None:
            self.src = DataModule.from_dict(raw_src)

        raw_dest = obj.get("dest")

        if raw_dest is not None:
            self.dest = DataModule.from_dict(raw_dest)
