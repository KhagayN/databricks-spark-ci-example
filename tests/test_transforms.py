"""Example Spark tests — intended to run ON Databricks (bundle job), not via local Maven/Delta.

Uses the notebook / job SparkSession (Delta already on DBR).
"""

from pyspark.sql import SparkSession

from src.transforms import filter_positive, with_amount_cents


def _spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def test_with_amount_cents():
    spark = _spark()
    df = spark.createDataFrame([(1.23,), (4.5,)], ["amount"])
    out = with_amount_cents(df).collect()
    by_amount = {row.amount: row.amount_cents for row in out}
    assert by_amount[1.23] == 123
    assert by_amount[4.5] == 450


def test_filter_positive():
    spark = _spark()
    df = spark.createDataFrame([(-1.0,), (0.0,), (2.0,)], ["amount"])
    assert filter_positive(df).count() == 1


def test_delta_roundtrip_tmp():
    """Smoke-test Delta without downloading JARs — DBR already has Delta."""
    spark = _spark()
    path = f"/tmp/spark-ci-example-delta-{spark.sparkContext.applicationId}"
    df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "label"])
    df.write.format("delta").mode("overwrite").save(path)
    back = spark.read.format("delta").load(path)
    assert back.count() == 2
