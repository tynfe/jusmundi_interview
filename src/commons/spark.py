from pyspark.sql import SparkSession

from commons.constant import (
    INGESTION_TABLE_NAME,
    RAW_SCHEMA,
    SILVER_SCHEMA,
    TRANSFORM_TABLE_NAME,
    INVALID_INGESTION_TABLE_NAME,
)


def create_spark_instance() -> SparkSession:
    return (
        SparkSession.builder.appName("jusmundi_number_ingestion")
        .config("kafka.group.id", "spark-consumer-group-jusmundi-new")
        .config(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.0",
        )
        .config("spark.sql.catalog.local.default-file-format", "parquet")
        .config("spark.sql.catalog.local.write.target-file-size-bytes", "134217728")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(f"spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.defaultCatalog", "lakehouse")
        .config(
            f"spark.sql.catalog.lakehouse.warehouse",
            f"s3a://adotmob-data-tests/Tyron/warehouse",
        )
        .config(f"spark.sql.catalog.lakehouse.type", "hive")
        .config(f"spark.sql.catalog.lakehouse.uri", "thrift://hive-metastore:9083")
        .config("spark.sql.catalog.lakehouse.parquet.compression-codec", "snappy")
        .config("streaming-skip-overwrite-snapshots", "true")
        .config("streaming-skip-delete-snapshots", "true")
        .getOrCreate()
    )


def create_schema_table(spark: SparkSession) -> None:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS lakehouse.{RAW_SCHEMA}")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS lakehouse.{RAW_SCHEMA}.{INGESTION_TABLE_NAME} (number INT, ingestion_ts TIMESTAMP, ingestion_hour STRING) USING iceberg PARTITIONED BY (days(ingestion_ts), ingestion_hour)"
    )
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS lakehouse.{RAW_SCHEMA}.{INVALID_INGESTION_TABLE_NAME} (invalid_number STRING, ingestion_ts TIMESTAMP, ingestion_hour STRING) USING iceberg PARTITIONED BY (days(ingestion_ts), ingestion_hour)"
    )

    spark.sql(f"CREATE SCHEMA IF NOT EXISTS lakehouse.{SILVER_SCHEMA}")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS lakehouse.{SILVER_SCHEMA}.{TRANSFORM_TABLE_NAME} (number INT, number_to_french STRING, transformation_ts TIMESTAMP) USING iceberg PARTITIONED BY (days(transformation_ts)) "
    )


def drop_table(spark: SparkSession) -> None:
    spark.sql("drop table lakehouse.raw.another_ingestion_number")
    spark.sql("drop table lakehouse.raw.numbers")
    spark.sql("drop table lakehouse.raw.invalid_numbers")
