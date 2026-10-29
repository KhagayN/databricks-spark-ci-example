# Paste-ready customer reply

The Maven failure is expected with the current setup. `delta-spark` / `configure_spark_with_delta_pip()` does **not** ship the Delta JARs. It sets `spark.jars.packages`, and Spark/Ivy then tries to pull them from Maven Central. If Maven is not on the GitHub runner allowlist, those tests cannot start.

That also is not the best CI shape for Spark written for Databricks. OSS PySpark + pip Delta will not match DBR (Spark, Delta, Unity Catalog).

**Recommended pattern:** GitHub Actions only orchestrates. Spark/Delta tests run **on Databricks**, where Delta is already on the runtime. The runner does not need Maven. Allowlist the **workspace URL** (and PyPI only if you use Databricks Connect), not `repo1.maven.org`.

Split tests:

1. Pure Python (no Spark) on the GitHub runner — fast, no JARs.
2. Spark/Delta tests as a Databricks Job from a bundle (`pytest` on serverless or a job cluster).
3. Optional: `databricks-connect` + `pytest` on the runner (PyPI, not Maven). Do not install both `pyspark` and `databricks-connect`.

Use a **service principal** (GitHub OIDC / workload identity federation preferred over PATs).

We put a minimal example repo together you can copy from: **databricks-spark-ci-example** (workflow + `databricks.yml` + pytest runner notebook).

Important: `spark_unit_tests` is the **job key in `databricks.yml`**, not a file. The tests are still `tests/test_*.py`; a small notebook task runs pytest on Databricks.

```yaml
# .github/workflows/databricks_spark_tests.yml (excerpt)
- uses: databricks/setup-cli@main
- run: databricks bundle validate -t ci
- run: databricks bundle deploy -t ci
- run: databricks bundle run spark_unit_tests -t ci
```

```yaml
# resources/spark_unit_tests.yml — job key == CLI argument
resources:
  jobs:
    spark_unit_tests:
      name: spark-unit-tests
      tasks:
        - task_key: pytest
          notebook_task:
            notebook_path: ../notebooks/run_unit_tests.py
```

`notebooks/run_unit_tests.py` installs pytest, runs it, and fails the job if the exit code is non-zero (`assert retcode == 0`).

**If CI still cannot reach the workspace** (last resort only): stop using `configure_spark_with_delta_pip()`, vendor the matching Delta JARs (and transitives) in Artifactory or the repo, and point Spark at them with `spark.jars`. Or allowlist your **internal Maven mirror** and set `spark.jars.repositories`. That will still diverge from DBR/UC, so we would not use it as the main path. See `docs/FALLBACK_VENDOR_JARS.md` in the example repo.

Docs / example workflows:
- GitHub Actions + `databricks bundle deploy` / `bundle run`: https://docs.databricks.com/aws/en/dev-tools/ci-cd/github
- pytest + Databricks Connect: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/testing
- Notebook pytest + GitHub Actions (`databricks/run-notebook`): https://docs.databricks.com/aws/en/notebooks/best-practices
- Notebook unit testing (`assert retcode == 0`): https://docs.databricks.com/aws/en/notebooks/testing
- Service principals for CI/CD: https://docs.databricks.com/aws/en/dev-tools/auth/service-principals

Happy to walk through a `ci` bundle target and the pytest runner notebook on a working session if useful.
