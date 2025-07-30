from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

BRONZE_METADATA_SCHEMA = StructType(
    [
        StructField("bronze_data_table", StringType(), False),
        StructField("source_system", StringType(), False),
        StructField("source_type", StringType(), False),
        StructField("source_name", StringType(), False),
        StructField("updated_at", TimestampType(), False),
    ]
)

BRONZE_LOG_SCHEMA = StructType(
    [
        StructField("ingested_timestamp", TimestampType(), False),
        StructField("source_name", StringType(), False),
        StructField("source_count", IntegerType(), False),
        StructField("bronze_data_table", StringType(), False),
        StructField("bronze_data_count", IntegerType(), False),
        StructField("status", StringType(), False),
    ]
)

SILVER_METADATA_SCHEMA = StructType(
    [
        StructField("silver_data_table", StringType(), False),
        StructField("bronze_data_table", StringType(), False),
        StructField("last_bronze_data_processed", TimestampType(), False),
        StructField("updated_at", TimestampType(), False),
    ]
)

SILVER_LOG_SCHEMA = StructType(
    [
        StructField("transformed_timestamp", TimestampType(), False),
        StructField("transformed_count", IntegerType(), False),
        StructField("silver_data_table", StringType(), False),
        StructField("silver_data_count", IntegerType(), False),
        StructField("status", StringType(), False),
    ]
)

GOLD_METADATA_SCHEMA = StructType(
    [
        StructField("gold_data_table", StringType(), False),
        StructField("silver_data_table", StringType(), False),
        StructField("last_silver_data_processed", TimestampType(), False),
        StructField("updated_at", TimestampType(), False),
    ]
)

GOLD_LOG_SCHEMA = StructType(
    [
        StructField("aggregated_timestamp", TimestampType(), False),
        StructField("gold_data_type", StringType(), False),
        StructField("gold_data_name", StringType(), False),
        StructField("gold_data_count", IntegerType(), False),
        StructField("aggregated_count", IntegerType(), False),
        StructField("status", StringType(), False),
    ]
)
