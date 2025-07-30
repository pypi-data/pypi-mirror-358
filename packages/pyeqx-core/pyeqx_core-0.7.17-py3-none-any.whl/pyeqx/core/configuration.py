from dataclasses import dataclass
from typing import Any, TypeVar

from pyeqx.core.common import to_dict
from pyeqx.core.models.app import App
from pyeqx.core.models.engine import Engine

T = TypeVar("T")


@dataclass
class Configuration:
    engine: Engine
    app: App

    @staticmethod
    def from_dict(obj: Any) -> "Configuration":
        assert isinstance(obj, dict)
        print("Configuration")
        engine = Engine.from_dict(obj.get("engine"))
        app = App.from_dict(obj.get("app"))
        return Configuration(engine, app)

    def to_dict(self) -> dict:
        result: dict = {}
        result["engine"] = to_dict(Engine, self.engine)
        result["app"] = to_dict(App, self.app)
        return result


def configuration_from_dict(obj: Any) -> Configuration:
    return Configuration.from_dict(obj)
