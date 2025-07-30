from logging import Logger
from typing import List, Optional, Union

from pyspark.sql import DataFrame, DataFrameWriter, functions as F

from pyeqx.core.common import SPARK_S3_PATH_PREFIX


class OperationWriter:
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    def write_to_s3(
        self,
        data: DataFrame,
        mode: str,
        path: str,
        options: Optional[dict],
        partition_by: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """
        Write data to S3 (Amazon S3) storage (or any compatible storage)

        ** Currently, support 'delta' format only **

        Args:
            data (DataFrame): data to write
            mode (str): support 'append' and 'overwrite'
            path (str): path to write data (e.g. 'bucket-name/folder-name/delta-table-name')
            options (Optional[dict]): additional options for writing data. Defaults to None.

        Notes:
            mergeSchema is set to False by default
        """

        if options is None:
            options = {}

        path_prefix = SPARK_S3_PATH_PREFIX

        actual_options = {"mergeSchema": False}
        actual_path = f"{path_prefix}{path}"

        for key, value in actual_options.items():
            options[key] = value

        if actual_path != "":
            self.write_to(
                data=data,
                format="delta",
                mode=mode,
                path=actual_path,
                options=options,
                partition_by=partition_by,
            )

    def write_to_mongodb(
        self,
        data: DataFrame,
        mode: str,
        uri: str,
        db: str,
        table: str,
        options: Optional[dict],
    ) -> None:
        """
        Write data to MongoDB storage

        Args:
            data (DataFrame): data to write
            mode (str): support 'append' and 'overwrite'
            uri (str): full connection uri
            db (str): database name
            table (str): collection name
            options (Optional[dict]): additional options for writing data. Defaults to None.
        """

        if options is None:
            options = {}

        spark_options = {
            "spark.mongodb.connection.uri": uri,
            "spark.mongodb.database": db,
            "spark.mongodb.collection": table,
        }

        options.update(spark_options)

        self.write_to(data=data, format="mongodb", mode=mode, options=options)

    def write_to_mssql(
        self,
        data: DataFrame,
        mode: str,
        url: str,
        table: str,
        options: Optional[dict],
    ) -> None:
        """
        Write data to MSSQL storage (Azure SQL Database, SQL Server, etc.)

        - using 'com.microsoft.sqlserver.jdbc.SQLServerDriver' as driver
        - 'overwrite' mode will drop the table and recreate it, to avoid drop table, add 'truncate=True' option.
        - batchsize is set to 1048576 by default
        - schemaCheckEnabled is set to False by default
        - tableLock is set to True by default

        Args:
            data (DataFrame): data to write
            mode (str): support 'append' and 'overwrite'
            url (str): _description_
            table (str): _description_
            options (Optional[dict]): _description_

        Notes:
            - change format back to 'jdbc' (default). To use 'com.microsoft.sqlserver.jdbc.spark',
              please use write_to_sql method instead and set format to 'com.microsoft.sqlserver.jdbc.spark'
        """

        if options is None:
            options = {}

        spark_options = {
            "url": url,
            "dbtable": table,
            "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "batchsize": 1048576,
            "schemaCheckEnabled": False,
            "tableLock": True,
        }

        options.update(spark_options)

        self.write_to_sql(
            data=data,
            mode=mode,
            options=options,
        )

    def write_to_postgresql(
        self,
        data: DataFrame,
        mode: str,
        url: str,
        table: str,
        options: Optional[dict],
    ) -> None:
        """
        Write data to PostgreSQL storage

        - using 'org.postgresql.Driver' as driver
        - 'overwrite' mode will drop the table and recreate it, to avoid drop table, add 'truncate=True' option.
        - batchsize is set to 1048576 by default
        - schemaCheckEnabled is set to False by default
        - tableLock is set to True by default

        Args:
            data (DataFrame): data to write
            mode (str): support 'append' and 'overwrite'
            url (str): full connection url
            table (str): table name
            options (Optional[dict]): additional options for writing data. Defaults to None.
        """

        if options is None:
            options = {}

        spark_options = {
            "url": url,
            "dbtable": table,
            "driver": "org.postgresql.Driver",
            "batchsize": 1048576,
            "schemaCheckEnabled": False,
            "tableLock": True,
        }

        options.update(spark_options)

        self.write_to_sql(
            data=data,
            mode=mode,
            options=options,
        )

    def write_to_sql(
        self,
        data: DataFrame,
        mode: str,
        format: str = "jdbc",
        options: dict = {},
    ) -> None:
        """
        Write data to SQL storage (PostgreSQL, MySQL, MSSQL, etc.)

        Args:
            data (DataFrame): data to write
            mode (str): support 'append' and 'overwrite'
            format (str, optional): format to write data. Defaults to "jdbc".
            options (dict, optional): additional options for writing data. Defaults to {}.
        """

        self.write_to(
            data=data,
            format=format,
            mode=mode,
            options=options,
        )

    def write_to_kafka(
        self,
        data: DataFrame,
        topic: str,
        is_override_message_transform: bool = False,
        options: Optional[dict] = None,
    ):
        """
        Write (produce) data to Kafka

        Args:
            data (DataFrame): data to write
        """

        self.__logger.debug(f"writing data to format: kafka, topic: {topic}.")

        if options is None:
            options = {}

        spark_options = {"topic": topic}
        spark_options.update(options)

        if not is_override_message_transform:
            wrapped_data = data
        else:
            wrapped_data = data.select(
                F.to_json(F.struct([data[x] for x in data.columns])).alias("value")
            )

        writer = wrapped_data.write.options(**spark_options).format("kafka")

        self.__do_write_to(writer=writer)

    def write_to(
        self,
        data: DataFrame,
        format: str,
        mode: str,
        path: Optional[str] = None,
        options: dict = {},
        partition_by: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """
        Write data to storage

        ** use with caution, this method is for custom/override logic to write data **

        Args:
            data (DataFrame): data to write
            format (str): format to write data
            mode (str): support 'append' and 'overwrite'
            path (str, optional): path to write data. Defaults to None.
            options (dict, optional): additional options for writing data. Defaults to {}.
        """

        self.__logger.debug(
            f"writing data to format: {format}, mode: {mode}, path: {path}."
        )

        writer = data.write.options(**options)

        modes = ["append", "overwrite"]

        parsed_mode = mode.lower()
        actual_mode = parsed_mode if parsed_mode in modes else "append"

        writer = writer.format(format).mode(actual_mode)
        if partition_by is not None:
            writer = writer.partitionBy(partition_by)

        self.__do_write_to(writer=writer, path=path)

    def __do_write_to(
        self,
        writer: DataFrameWriter,
        path: Optional[str] = None,
    ):
        writer.save(path)
