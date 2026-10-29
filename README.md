# Databricks Spark CI example (Maven-free)

**Repo:** https://github.com/KhagayN/databricks-spark-ci-example

Example pattern for testing Spark / Delta code written for Databricks when **GitHub runners cannot reach Maven Central**.

## The problem

Local OSS PySpark + `delta-spark` often uses `configure_spark_with_delta_pip()`, which sets `spark.jars.packages`. Spark/Ivy then downloads Delta JARs from Maven. Locked-down runners that do not allowlist Maven fail before tests run.

That local stack is also a poor match for Databricks Runtime (Spark, Delta, Unity Catalog).

## Recommended pattern

**GitHub Actions only orchestrates. Spark / Delta tests run on Databricks**, where Delta is already on the runtime. The runner does not need Maven.

Allowlist:

- Databricks workspace URL
- PyPI (only if you use Databricks Connect)

Do **not** require `repo1.maven.org`.

### Test layers

1. **Pure Python** (no Spark) on the GitHub runner — optional, fast.
2. **Spark / Delta** as a Databricks Job from a Databricks Asset Bundle (`pytest` on serverless or a job cluster).
3. **Optional:** `databricks-connect` + `pytest` on the runner (PyPI, not Maven). Do not install both `pyspark` and `databricks-connect`.

Use a **service principal**. Prefer GitHub OIDC / workload identity federation over PATs.

## What `spark_unit_tests` is

`spark_unit_tests` is the **job key** in [`databricks.yml`](databricks.yml) — the name passed to `databricks bundle run spark_unit_tests`. It is **not** a file.

| Path | Role |
|------|------|
| `databricks.yml` | Defines job key `spark_unit_tests` |
| `tests/test_*.py` | Real pytest files |
| `notebooks/run_unit_tests.py` | Notebook task that installs pytest and fails the job if exit code ≠ 0 |

## Quick start

1. Copy this repo (or the relevant files) into your project.
2. Create a Databricks service principal and grant it rights to deploy/run the `ci` target.
3. In GitHub Actions secrets/vars:
   - `DATABRICKS_HOST` — workspace URL
   - `DATABRICKS_CLIENT_ID` — service principal UUID (OIDC), **or**
   - `DATABRICKS_TOKEN` — SP token if OIDC is not ready yet
4. Update `targets.ci.workspace.host` in `databricks.yml`.
5. Open a PR; the workflow validates, deploys the `ci` target, and runs `spark_unit_tests`.

### Local dry-run (from a machine that can reach the workspace)

```bash
databricks bundle validate -t ci
databricks bundle deploy -t ci
databricks bundle run spark_unit_tests -t ci
```

## Last resort: runner-local Spark without Maven

Only if CI cannot reach the workspace:

1. Stop using `configure_spark_with_delta_pip()`.
2. Vendor matching Delta JARs (and transitives) in Artifactory or the repo.
3. Point Spark at them with `spark.jars` plus the usual Delta session configs.

Or allowlist an **internal Maven mirror** and set `spark.jars.repositories`. This will diverge from DBR / UC — not the main path.

## Docs

- [GitHub Actions + bundles](https://docs.databricks.com/aws/en/dev-tools/ci-cd/github)
- [pytest + Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/testing)
- [Notebook best practices (GitHub Actions)](https://docs.databricks.com/aws/en/notebooks/best-practices)
- [Notebook unit testing](https://docs.databricks.com/aws/en/notebooks/testing)
- [Service principals for CI/CD](https://docs.databricks.com/aws/en/dev-tools/auth/service-principals)

Azure: replace `/aws/` with `/azure/` in those URLs.
