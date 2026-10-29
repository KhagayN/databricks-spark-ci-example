# Databricks notebook source
# MAGIC %md
# MAGIC # Spark unit test runner
# MAGIC
# MAGIC Invoked by the `spark_unit_tests` **job** (job key in the bundle — not a file).
# MAGIC Runs pytest on Databricks Runtime so Delta JARs are already present (no Maven).

# COMMAND ----------

# MAGIC %pip install pytest -q
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import sys
from pathlib import Path

# Skip writing pyc files on a readonly filesystem.
sys.dont_write_bytecode = True

# Bundle syncs the repo under the workspace file_path. Prefer the notebook's folder parent.
here = Path.cwd()
candidates = [here, here.parent, Path("/Workspace")]
repo_root = next(
    (p for p in candidates if (p / "tests").is_dir() and (p / "src").is_dir()),
    here,
)
sys.path.insert(0, str(repo_root))
test_dir = repo_root / "tests"

import pytest

retcode = pytest.main(
    [
        str(test_dir),
        "-v",
        "-p",
        "no:cacheprovider",
    ]
)

assert retcode == 0, "The pytest invocation failed. See the log for details."
