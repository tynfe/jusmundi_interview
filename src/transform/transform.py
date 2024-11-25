import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, days, col, lit, to_date
from pyspark.sql.types import StringType

from commons.constant import (
    INGESTION_TABLE_NAME,
    TRANSFORM_TABLE_NAME,
    SILVER_SCHEMA,
    RAW_SCHEMA,
)


def number_to_french_text(number: int) -> str:
    """
     number_to_french_text take a number as a parameter and transform it in French following multiples rules.
     Disclaimer : This function is defined in transform.py and should be there but because I face challenge running it on the
     spark cluster I decided to put it there just for the run.
    :param number: the number to translate
    :return : the stringify number
    """
    units = [
        "zéro",
        "un",
        "deux",
        "trois",
        "quatre",
        "cinq",
        "six",
        "sept",
        "huit",
        "neuf",
    ]
    teens = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize"]
    tens = ["", "dix", "vingt", "trente", "quarante", "cinquante", "soixante"]

    if number < 17:
        return units[number] if number < 10 else teens[number - 10]

    if number < 70:
        tens_digit, unit_digit = divmod(number, 10)
        return (
            tens[tens_digit]
            + ("-et-" if unit_digit == 1 and tens_digit > 1 else "-")
            + units[unit_digit]
            if unit_digit > 0
            else tens[tens_digit]
        )

    if number < 80:
        if number == 70:
            return "septante"
        if number == 71:
            return "soixante-et-onze"
        return "soixante-" + number_to_french_text(number - 60)

    if number < 100:
        if number == 80:
            return "huitante"
        if number == 90:
            return "nonante"

        return "quatre-vingt" + (
            "-" + number_to_french_text(number - 80) if number != 80 else "s"
        )

    if number < 1000:
        hundreds_digit, remainder = divmod(number, 100)
        return (
            (units[hundreds_digit] + "-cent" + ("s" if remainder == 0 else ""))
            + ("-" + number_to_french_text(remainder) if remainder > 0 else "")
            if hundreds_digit > 1
            else "cent"
            + ("-" + number_to_french_text(remainder) if remainder > 0 else "")
        )

    thousands_digit, remainder = divmod(number, 1000)
    return (units[thousands_digit] + "-mille" if thousands_digit > 1 else "mille") + (
        "-" + number_to_french_text(remainder) if remainder > 0 else ""
    )


def transform(spark: SparkSession, start_date: str, current_hour: str):
    """
    register an udf that transform number to text
    :param spark: spark session
    :param start_date: start date to filter table partition
    :param current_hour: current hour to process
    :return:
    """
    number_to_french_text_udf = udf(number_to_french_text, StringType())

    df = spark.table(f"lakehouse.{RAW_SCHEMA}.{INGESTION_TABLE_NAME}")
    df = df.where(
        (to_date(col("ingestion_ts")) == lit(start_date))
        & (col("ingestion_hour") == lit(current_hour))
    )

    df_with_text = (
        df.drop("ingestion_ts", "ingestion_hour")
        .withColumn("number_to_french", number_to_french_text_udf(df["number"]))
        .withColumn("transformation_ts", lit(datetime.datetime.now()))
    )
    df_with_text.printSchema()

    partitions = [col("number"), days(col("transformation_ts"))]

    df_with_text.sortWithinPartitions(*partitions).writeTo(
        f"lakehouse.{SILVER_SCHEMA}.{TRANSFORM_TABLE_NAME}"
    ).using("iceberg").partitionedBy(*partitions).append()
