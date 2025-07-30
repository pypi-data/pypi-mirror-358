from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_bool, from_int, from_str


@dataclass
class Engine:
    storage: str
    tmp_path: str

    is_dedicated_spark: bool
    spark_executor_core: int
    spark_executor_memory: str
    spark_endpoint: str

    is_dynamic_allocation: bool
    spark_executor_min_instances: int
    spark_executor_max_instances: int

    spark_options: dict

    spark_maven_repositories: list[str]

    @staticmethod
    def from_dict(obj: Any) -> "Engine":
        assert isinstance(obj, dict)
        storage = from_str(obj.get("storage"))
        tmp_path = from_str(obj.get("tmpPath"))
        is_dedicated_spark = from_bool(obj.get("isDedicatedSpark"))
        spark_executor_core = from_int(obj.get("sparkExecutorCore"))
        spark_executor_memory = from_str(obj.get("sparkExecutorMemory"))

        raw_spark_endpoint = obj.get("sparkEndpoint")
        spark_endpoint = (
            "" if raw_spark_endpoint is None else from_str(raw_spark_endpoint)
        )

        is_dynamic_allocation = from_bool(obj.get("isDynamicAllocation"))
        spark_executor_min_instances = from_int(obj.get("sparkExecutorMinInstances"))
        spark_executor_max_instances = from_int(obj.get("sparkExecutorMaxInstances"))

        raw_spark_options = obj.get("sparkOptions")

        spark_options = (
            raw_spark_options
            if raw_spark_options is not None and isinstance(raw_spark_options, dict)
            else {}
        )

        spark_maven_repositories = obj.get("sparkMavenRepositories", [])

        return Engine(
            storage,
            tmp_path,
            is_dedicated_spark,
            spark_executor_core,
            spark_executor_memory,
            spark_endpoint,
            is_dynamic_allocation,
            spark_executor_min_instances,
            spark_executor_max_instances,
            spark_options,
            spark_maven_repositories,
        )
