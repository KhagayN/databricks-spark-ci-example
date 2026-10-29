# Last resort: runner-local Spark without Maven

Use this **only** if CI cannot reach a Databricks workspace.

## Why the default `delta-spark` path fails

`configure_spark_with_delta_pip()` sets `spark.jars.packages` to Maven coordinates.
Spark then downloads JARs. No Maven allowlist → tests never start.

## Workaround

1. Stop calling `configure_spark_with_delta_pip()`.
2. Download the Delta JARs (and transitive deps) that match your Spark/Scala version
   from a machine that *can* reach Maven, or from your Artifactory mirror.
3. Place them in `vendor/jars/` (or point at Artifactory URLs your runner can reach).
4. Configure the session with local paths:

```python
from pyspark.sql import SparkSession

delta_jar = "/path/to/vendor/jars/delta-spark_2.12-3.x.x.jar"  # match your versions

spark = (
    SparkSession.builder.master("local[*]")
    .appName("ci-local")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
    .config("spark.jars", f"file://{delta_jar}")
    .getOrCreate()
)
```

Or allowlist an **internal** Maven mirror and set `spark.jars.repositories` to that mirror
(not public Maven Central).

## Caveats

- Version skew vs Databricks Runtime
- Unity Catalog APIs will not match
- JAR licensing and size in git/Artifactory

Prefer the main path: run Spark tests on Databricks via the bundle job in this repo.
