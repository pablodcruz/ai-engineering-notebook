from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


SQL_ROOT = Path("/opt/streamflow-analytics/sql")
SNOWFLAKE_CONN_ID = "streamflow_snowflake"


def sql_file(relative_path: str) -> str:
    return (SQL_ROOT / relative_path).read_text(encoding="utf-8")


def validate_required_sql_files() -> None:
    required = [
        "bronze/create_bronze_tables.sql",
        "bronze/load_bronze_events_from_parquet.sql",
        "silver/create_silver_tables.sql",
        "silver/transform_silver_events.sql",
        "silver/quality_checks.sql",
        "gold/create_gold_tables.sql",
        "gold/build_dimensions.sql",
        "gold/build_fact_events.sql",
        "gold/build_domain_metrics.sql",
    ]
    missing = [path for path in required if not (SQL_ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(f"Missing StreamFlow SQL files: {missing}")


with DAG(
    dag_id="streamflow_phase_2_snowflake_pipeline",
    description="Load StreamFlow Phase 1 output into Snowflake medallion layers and Gold BI tables.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streamflow", "snowflake", "analytics"],
) as dag:
    start = EmptyOperator(task_id="start")

    check_source_contract = PythonOperator(
        task_id="check_source_contract",
        python_callable=validate_required_sql_files,
    )

    create_bronze = SQLExecuteQueryOperator(
        task_id="create_bronze_objects",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("bronze/create_bronze_tables.sql"),
    )

    load_bronze_events = SQLExecuteQueryOperator(
        task_id="load_bronze_events",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("bronze/load_bronze_events_from_parquet.sql"),
    )

    create_silver = SQLExecuteQueryOperator(
        task_id="create_silver_objects",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("silver/create_silver_tables.sql"),
    )

    run_silver_transformations = SQLExecuteQueryOperator(
        task_id="run_silver_transformations",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("silver/transform_silver_events.sql"),
    )

    run_quality_checks = SQLExecuteQueryOperator(
        task_id="run_quality_checks",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("silver/quality_checks.sql"),
    )

    create_gold = SQLExecuteQueryOperator(
        task_id="create_gold_objects",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("gold/create_gold_tables.sql"),
    )

    build_gold_dimensions = SQLExecuteQueryOperator(
        task_id="build_gold_dimensions",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=sql_file("gold/build_dimensions.sql"),
    )

    build_gold_facts = SQLExecuteQueryOperator(
        task_id="build_gold_facts",
        conn_id=SNOWFLAKE_CONN_ID,
        sql=[
            sql_file("gold/build_fact_events.sql"),
            sql_file("gold/build_domain_metrics.sql"),
        ],
    )

    publish_run_summary = EmptyOperator(task_id="publish_run_summary")

    (
        start
        >> check_source_contract
        >> create_bronze
        >> load_bronze_events
        >> create_silver
        >> run_silver_transformations
        >> run_quality_checks
        >> create_gold
        >> build_gold_dimensions
        >> build_gold_facts
        >> publish_run_summary
    )
