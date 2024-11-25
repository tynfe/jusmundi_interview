from pyspark.sql.functions import udf, days, col, lit, now, to_date
from pyspark.sql.types import StringType

from commons.constant import (
    INGESTION_TABLE_NAME,
    TRANSFORM_TABLE_NAME,
    SILVER_SCHEMA,
    RAW_SCHEMA,
)
from commons.spark import create_schema_table, create_spark_instance
from extract.extract import extract
from parser.argument import parser


def number_to_french_text(number: int) -> str:
    """
     number_to_french_text take a number as a parameter and transform it in French following multiples rules.
     DISCLAIMER !!!!! : This function is defined in transform.py and should be defined there only but because I faced challenges running it on the
     cluster spark I decided to put it there just to run it successfully.
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


if __name__ == "__main__":
    args = parser.parse_args()

    spark = create_spark_instance()
    create_schema_table(spark)

    if args.runner == "extract":
        extract(spark)

    elif args.runner == "transform":

        # simulate airflow dag scheduling

        number_to_french_text_udf = udf(number_to_french_text, StringType())

        df = spark.table(f"lakehouse.{RAW_SCHEMA}.{INGESTION_TABLE_NAME}")
        df.show()

        df = df.where(
            (to_date(col("ingestion_ts")) == lit("2024-11-25"))
            & (col("ingestion_hour") == lit(12))
        )
        # here we are specifying 12 and '2024-11-25' because we are targeting the
        # partition where data is written

        df_with_text = (
            df.drop("ingestion_ts", "ingestion_hour")
            .withColumn("number_to_french", number_to_french_text_udf(df["number"]))
            .withColumn("transformation_ts", now())
        )

        partitions = [col("number"), days(col("transformation_ts"))]

        df_with_text.sortWithinPartitions(*partitions).writeTo(
            f"lakehouse.{SILVER_SCHEMA}.{TRANSFORM_TABLE_NAME}"
        ).using("iceberg").partitionedBy(*partitions).append()
