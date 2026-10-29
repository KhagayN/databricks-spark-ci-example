"""Sample transforms used by the example tests.

These run on Databricks Runtime in CI — use the built-in spark session / Delta APIs,
not OSS PySpark + configure_spark_with_delta_pip().
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def with_amount_cents(df: DataFrame, amount_col: str = "amount") -> DataFrame:
    """Add amount_cents = round(amount * 100) as a long."""
    return df.withColumn(
        "amount_cents",
        F.round(F.col(amount_col) * 100).cast("long"),
    )


def filter_positive(df: DataFrame, amount_col: str = "amount") -> DataFrame:
    return df.filter(F.col(amount_col) > 0)
