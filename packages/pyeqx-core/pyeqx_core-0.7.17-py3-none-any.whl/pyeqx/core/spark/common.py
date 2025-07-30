from typing import Any, Dict, Iterable
import os

from pyeqx.core.constants import SPARK_DEFAULT_PACKAGES
from pyeqx.core.configuration import Configuration
from pyeqx.core.enums import DataType
from pyeqx.core.errors import StorageNotSupportedException
from pyeqx.core.models.storage.properties import (
    S3DataProperties,
)

from delta import configure_spark_with_delta_pip
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType

SPARK_EXECUTOR_NAMESPACE_KEY = "SPARK_EXECUTOR_NAMESPACE"
SPARK_EXECUTOR_IMAGE_KEY = "SPARK_EXECUTOR_IMAGE"
SPARK_EXECUTOR_NODE_SELECTOR_LABEL_KEY = "SPARK_EXECUTOR_NODE_SELECTOR_LABEL"
SPARK_EXECUTOR_NODE_SELECTOR_VALUE_KEY = "SPARK_EXECUTOR_NODE_SELECTOR_VALUE"

SPARK_MONITOR_ENABLED_KEY = "SPARK_MONITOR_ENABLED"

DEFAULT_SPARK_EXECUTOR_NAMESPACE = "data-driven-dd30"
DEFAULT_SPARK_EXECUTOR_IMAGE = (
    "acrdisazassedev001.azurecr.io/esbm-dis-datadriven-spark-py-develop:cb43ab8"
)

DEFAULT_MAVEN_REPOSITORIES = [
    "https://pkgs.dev.azure.com/solytic/OpenSource/_packaging/releases/maven/v1"
]

SPARK_AZURE_STORAGE_ACCOUNT_URL = "SPARK_AZURE_STORAGE_ACCOUNT_URL"
SPARK_AZURE_STORAGE_ACCOUNT_KEY = "SPARK_AZURE_STORAGE_ACCOUNT_KEY"

SPARK_S3A_ENDPOINT = "SPARK_S3A_ENDPOINT"
SPARK_S3A_ACCESS_KEY = "SPARK_S3A_ACCESS_KEY"
SPARK_S3A_SECRET_KEY = "SPARK_S3A_SECRET_KEY"


def build_options(
    host_ip: str, config: Configuration, options: dict[str, Any]
) -> Dict[str, Any]:
    # engine: object storage configuration
    engine_storage = config.app.storages.get("system")

    spark_executor_core = config.engine.spark_executor_core
    spark_executor_memory = config.engine.spark_executor_memory

    is_dynamic_allocation = config.engine.is_dynamic_allocation
    spark_executor_min_instances = config.engine.spark_executor_min_instances
    spark_executor_max_instances = config.engine.spark_executor_max_instances

    spark_namespace = os.environ.get(
        SPARK_EXECUTOR_NAMESPACE_KEY, DEFAULT_SPARK_EXECUTOR_NAMESPACE
    )
    spark_image = os.environ.get(SPARK_EXECUTOR_IMAGE_KEY, DEFAULT_SPARK_EXECUTOR_IMAGE)
    spark_node_selector_label = os.environ.get(
        SPARK_EXECUTOR_NODE_SELECTOR_LABEL_KEY, None
    )
    spark_node_selector_value = os.environ.get(
        SPARK_EXECUTOR_NODE_SELECTOR_VALUE_KEY, None
    )

    actual_maven_repositories = list(
        set(DEFAULT_MAVEN_REPOSITORIES + config.engine.spark_maven_repositories)
    )

    spark_home = os.environ.get("SPARK_HOME", "/usr/local/spark")

    spark_config = {
        "spark.master": (
            config.engine.spark_endpoint
            if config.engine.is_dedicated_spark
            else "k8s://https://kubernetes.default.svc.cluster.local"
        ),
        "spark.driver.blockManager.port": "7777",
        "spark.driver.port": "2222",
        "spark.driver.host": host_ip,
        "spark.driver.bindAddress": "0.0.0.0",
        "spark.sql.caseSensitive": True,
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension,com.datastax.spark.connector.CassandraSparkExtensions",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.sql.inMemoryColumnarStorage.compressed": True,
        "spark.sql.execution.arrow.pyspark.enabled": True,
        "spark.jars.repositories": ",".join(actual_maven_repositories),
        "spark.executorEnv.LD_LIBRARY_PATH": "/opt/spark/work-dir/:$LD_LIBRARY_PATH",
        "spark.executorEnv.LOG4J_LEVEL": "INFO",
        "spark.executorEnv.SPARK_USER": "spark",
        "spark.executorEnv.SPARK_LOG_LEVEL": "INFO",
    }

    if engine_storage.type == DataType.S3:
        spark_config = __apply_hadoop_s3a_options(
            config=spark_config,
            options=options,
            props=engine_storage.get_properties(cls=S3DataProperties),
        )
    elif engine_storage.type == DataType.AzureAdlsGen2Storage:
        spark_config = __apply_hadoop_adls_gen2_options(
            config=spark_config,
            options=options,
        )
    else:
        raise StorageNotSupportedException(storage=engine_storage)

    is_airflow_execution = os.environ.get("AIRFLOW_EXECUTION", "false").lower() in (
        "true",
    )

    is_spark_monitor_enabled = __parse_monitor_enabled_option(options=options)

    if is_spark_monitor_enabled and not is_airflow_execution:
        spark_config.update(
            {
                "spark.extraListeners": "sparkmonitor.listener.JupyterSparkMonitorListener",
                "spark.driver.extraClassPath": f"{spark_home}/jars/sparkmonitor-listener.jar",
            }
        )

    if not config.engine.is_dedicated_spark:
        spark_config.update(
            {
                "spark.kubernetes.namespace": spark_namespace,
                "spark.kubernetes.container.image": spark_image,
                "spark.dynamicAllocation.shuffleTracking.enabled": "true",
                "spark.dynamicAllocation.enabled": is_dynamic_allocation,
                "spark.dynamicAllocation.maxExecutors": spark_executor_max_instances,
                "spark.executor.instances": spark_executor_min_instances,
                "spark.executor.memory": spark_executor_memory,
                "spark.executor.cores": spark_executor_core,
            }
        )

        if (
            spark_node_selector_label is not None
            and spark_node_selector_value is not None
        ):
            spark_config[
                f"spark.kubernetes.executor.node.selector.{spark_node_selector_label}"
            ] = spark_node_selector_value

    return spark_config


def get_session(
    app_name: str,
    config: dict,
    packages: Iterable[str] = [],
    options: dict = {},
) -> SparkSession:
    conf = SparkConf()

    for key, value in config.items():
        conf.set(key, value)

    for key, value in options.items():
        conf.set(key, value)

    default_packages = SPARK_DEFAULT_PACKAGES

    combined_packages: list[str] = default_packages + packages

    selected_packages = {}

    for package in combined_packages:
        parts = package.split(":")
        key = parts[0] + ":" + parts[1]

        selected_packages[key] = parts[2]

    actual_packages = [f"{key}:{value}" for key, value in selected_packages.items()]

    builder = SparkSession.builder.appName(app_name).config(conf=conf)

    # wait for deltalake to update its version (https://github.com/delta-io/delta/issues/889)
    return configure_spark_with_delta_pip(builder, actual_packages).getOrCreate()


def create_dataframe(
    spark: SparkSession, schema: StructType, datas: Iterable[Any] = []
) -> DataFrame:
    return spark.createDataFrame(datas, schema=schema)


def write_dataframe(df: DataFrame, path: str, options: dict):
    actual_options = {
        "mergeSchema": True,
    }

    write_df = df.write.format("delta").mode("append")

    actual_options.update(options)

    for key, value in actual_options.items():
        write_df.option(key, value)

    write_df.save(path)


def is_bucket_exist(context: SparkContext, bucket_name: str) -> bool:
    path = context._jvm.org.apache.hadoop.fs.FileSystem.get(
        context._jvm.java.net.URI.create(bucket_name),
        context._jsc.hadoopConfiguration(),
    )

    return path.exists(context._jvm.org.apache.hadoop.fs.Path(bucket_name))


def __apply_hadoop_s3a_options(
    config: dict[str, str], options: dict[str, str], props: S3DataProperties
):
    """
    Apply hadoop options for S3A.
    via endpoint, access_key, secret_key

    This will use environment variables first then options to override

    Variables:

     - "SPARK_S3A_ENDPOINT" as endpoint
     - "SPARK_S3A_ACCESS_KEY" as access_key
     - "SPARK_S3A_SECRET_KEY" as secret_key

    Args:
        config (dict[str, str]): Spark configuration
        options (dict[str, str]): Override options for Spark configuration

    Returns:
        config (dict[str, str]): Spark configuration that applied hadoop options
    """

    endpoint = os.environ.get(SPARK_S3A_ENDPOINT, "")
    access_key = os.environ.get(SPARK_S3A_ACCESS_KEY, "")
    secret_key = os.environ.get(SPARK_S3A_SECRET_KEY, "")

    # TODO: backward compatibility for using properties via configuration file. this need to be removed in the future.
    if endpoint == "":
        endpoint = props.endpoint
        access_key = props.access_key
        secret_key = props.secret_key

    config.update(
        {
            "spark.hadoop.fs.s3a.endpoint": endpoint,
            # "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.hadoop.fs.s3a.access.key": access_key,
            "spark.hadoop.fs.s3a.secret.key": secret_key,
        }
    )

    return config


def __apply_hadoop_adls_gen2_options(config: dict[str, str], options: dict[str, str]):
    """
    Apply hadoop options for Azure Data Lake Storage Gen2.
    via account_name and account_key

    This will use environment variable "SPARK_AZURE_STORAGE_ACCOUNT_URL" as key name and "SPARK_AZURE_STORAGE_ACCOUNT_KEY" as value first
    then use options as override value.

    e.g.

    - SPARK_AZURE_STORAGE_ACCOUNT_URL=fs.azure.account.key.{ACCOUNT_NAME}.dfs.core.windows.net
    - SPARK_AZURE_STORAGE_ACCOUNT_KEY={ACCOUNT_KEY}

    { "fs.azure.account.key.{ACCOUNT_NAME}.dfs.core.windows.net": "{ACCOUNT_KEY}" }

    Args:
        config (dict[str, str]): Spark configuration
        options (dict[str, str]): Override options for Spark configuration

    Returns:
        config (dict[str, str]): Spark configuration that applied hadoop options
    """

    key = options.get("azureKey", os.environ.get(SPARK_AZURE_STORAGE_ACCOUNT_URL, ""))
    value = options.get(
        "azureValue", os.environ.get(SPARK_AZURE_STORAGE_ACCOUNT_KEY, "")
    )

    config.update({key: value})

    return config


def __parse_monitor_enabled_option(options: dict[str, Any]):
    value = str(
        options.get(
            "isMonitorEnabled",
            os.environ.get(SPARK_MONITOR_ENABLED_KEY, "false").lower(),
        )
    )

    return value in ("true")
