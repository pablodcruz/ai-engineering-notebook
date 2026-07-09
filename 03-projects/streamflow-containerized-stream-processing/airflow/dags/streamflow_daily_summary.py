from __future__ import annotations

from datetime import datetime
import os

from airflow import DAG
from airflow.operators.bash import BashOperator


STREAMFLOW_HOME = os.getenv("STREAMFLOW_HOME", "/opt/streamflow")
SUMMARY_OUTPUT = os.getenv("STREAMFLOW_SUMMARY_OUTPUT", f"{STREAMFLOW_HOME}/data/curated/daily_summary")


with DAG(
    dag_id="streamflow_daily_summary",
    description="Run bounded StreamFlow Spark summary and validate output.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streamflow", "spark", "phase-1"],
) as dag:
    run_summary = BashOperator(
        task_id="run_spark_daily_summary",
        bash_command=(
            f"cd {STREAMFLOW_HOME} && "
            "spark-submit spark/jobs/daily_summary.py "
            "--input ${STREAMFLOW_RAW_OUTPUT:-data/raw/events} "
            "--output ${STREAMFLOW_SUMMARY_OUTPUT:-data/curated/daily_summary}"
        ),
    )

    validate_output = BashOperator(
        task_id="validate_summary_output",
        bash_command=f"test -d {SUMMARY_OUTPUT} && find {SUMMARY_OUTPUT} -type f | head -n 1",
    )

    run_summary >> validate_output

