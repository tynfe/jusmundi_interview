import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit, when, col, date_format
from statsd import StatsClient

from commons.constant import (
    RAW_SCHEMA,
    INGESTION_TABLE_NAME,
    INVALID_INGESTION_TABLE_NAME,
    INGESTION_TOPIC,
    INGESTION_GAUGE_NAME,
    INGESTION_INVALID_GAUGE_NAME,
)


def process_batch(batch_df: DataFrame, batch_id):
    metric = StatsClient(host="172.25.0.20", port=8125)

    valid_rows = batch_df.filter(col("number").isNotNull())
    invalid_rows = batch_df.filter(col("number").isNull())

    count = valid_rows.count()
    print(f"Batch {batch_id} has {count} records")

    metric.incr(INGESTION_GAUGE_NAME, count)
    metric.incr(INGESTION_INVALID_GAUGE_NAME, invalid_rows.count())

    valid_rows.drop("value").writeTo(
        f"lakehouse.{RAW_SCHEMA}.{INGESTION_TABLE_NAME}"
    ).append()

    invalid_rows.withColumnRenamed("value", "invalid_number").drop("number").writeTo(
        f"lakehouse.{RAW_SCHEMA}.{INVALID_INGESTION_TABLE_NAME}"
    ).append()


def stream_number_to_raw(
    bootstrap_server: str, topic: str, spark: SparkSession, offset: str = "earliest"
) -> None:
    number_ingestion_stream: DataFrame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_server)
        .option("subscribe", topic)
        .option("startingOffsets", offset)
        .load()
    )

    number_ingestion_df = (
        number_ingestion_stream.selectExpr("CAST(value AS STRING) AS value")
        .withColumn(
            "number",
            when(
                col("value").cast("INT").isNotNull(), col("value").cast("INT")
            ).otherwise(None),
        )
        .withColumn("ingestion_ts", lit(datetime.datetime.now()))
        .withColumn("ingestion_hour", date_format(col("ingestion_ts"), "HH"))
    )

    query = (
        number_ingestion_df.writeStream.foreachBatch(process_batch)
        .trigger(processingTime="1 minute")
        .option("fanout-enabled", "true")
        .option("checkpointLocation", ".local_checkpoint")
        .start()
    )

    query.awaitTermination()


def extract(
    spark: SparkSession,
    bootstrap: str = "kafka1:9093,kafka2:9092",
    topic: str = INGESTION_TOPIC,
) -> None:
    stream_number_to_raw(bootstrap, topic, spark)
