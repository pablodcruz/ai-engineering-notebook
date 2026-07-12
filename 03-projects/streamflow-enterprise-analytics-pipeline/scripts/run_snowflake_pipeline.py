from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path

from snowflake_smoke_test import clear_proxy_environment, connection_kwargs, load_env_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
PHASE1_SRC = REPO_ROOT / "03-projects" / "streamflow-containerized-stream-processing" / "src"


SQL_FILES = [
    "sql/bronze/create_bronze_tables.sql",
    "sql/silver/create_silver_tables.sql",
    "sql/gold/create_gold_tables.sql",
]

TRANSFORM_FILES = [
    "sql/bronze/load_bronze_events.sql",
    "sql/silver/transform_silver_events.sql",
    "sql/silver/quality_checks.sql",
    "sql/gold/build_dimensions.sql",
    "sql/gold/build_fact_events.sql",
    "sql/gold/build_domain_metrics.sql",
    "tests/reconciliation_checks.sql",
]

DEMO_TABLES = [
    "STREAMFLOW_DB.GOLD.FACT_COMMERCE_METRICS",
    "STREAMFLOW_DB.GOLD.FACT_EVENTS",
    "STREAMFLOW_DB.GOLD.DIM_ENTITY",
    "STREAMFLOW_DB.GOLD.DIM_EVENT_TYPE",
    "STREAMFLOW_DB.GOLD.DIM_DATE",
    "STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS",
    "STREAMFLOW_DB.SILVER.SILVER_EVENTS",
    "STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the StreamFlow Phase 2 Snowflake demo pipeline."
    )
    parser.add_argument(
        "--env-file", type=Path, required=True, help="Local env file with SNOWFLAKE_* values."
    )
    parser.add_argument(
        "--count", type=int, default=250, help="Number of synthetic Phase 1 events to generate."
    )
    parser.add_argument(
        "--invalid-rate", type=float, default=0.08, help="Fraction of generated invalid events."
    )
    parser.add_argument("--seed", type=int, default=13, help="Synthetic event seed.")
    parser.add_argument(
        "--reset-demo", action="store_true", help="Truncate StreamFlow demo tables before loading."
    )
    parser.add_argument(
        "--load-mode",
        choices=("insert", "stage"),
        default="insert",
        help="Load generated events by direct Bronze inserts or Snowflake stage PUT/COPY.",
    )
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Clear proxy environment variables for this process.",
    )
    return parser


def split_sql(sql: str) -> list[str]:
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def execute_sql_file(cursor, relative_path: str) -> list[tuple[str, list[tuple]]]:
    results: list[tuple[str, list[tuple]]] = []
    sql = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
    for statement in split_sql(sql):
        print(f"Executing {relative_path}: {statement.splitlines()[0][:96]}", flush=True)
        cursor.execute(statement)
        if statement.lstrip().upper().startswith("SELECT"):
            results.append((statement.splitlines()[0], cursor.fetchall()))
    return results


def generate_sample(path: Path, *, count: int, seed: int, invalid_rate: float) -> list[dict]:
    sys.path.insert(0, str(PHASE1_SRC))
    from streamflow.producer import generate_events, write_jsonl

    events = generate_events(count, seed=seed, invalid_rate=invalid_rate)
    write_jsonl(events, path)
    return events


def run_setup(cursor) -> None:
    for relative_path in SQL_FILES:
        execute_sql_file(cursor, relative_path)


def reset_demo_tables(cursor) -> None:
    for table in DEMO_TABLES:
        cursor.execute(f"TRUNCATE TABLE IF EXISTS {table}")


def stage_sample_file(cursor, sample_path: Path) -> None:
    cursor.execute(
        "REMOVE @STREAMFLOW_DB.BRONZE.STREAMFLOW_STAGE PATTERN = '.*streamflow_events.*'"
    )
    normalized = sample_path.resolve().as_posix()
    cursor.execute(
        f"PUT 'file://{normalized}' @STREAMFLOW_DB.BRONZE.STREAMFLOW_STAGE "
        "AUTO_COMPRESS = FALSE OVERWRITE = TRUE"
    )


def insert_bronze_events(cursor, events: list[dict]) -> None:
    statement = """
    INSERT INTO STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW (
      raw_payload,
      source_file,
      source_row_number,
      stream_topic,
      ingest_run_id
    )
    SELECT
      PARSE_JSON(%s),
      %s,
      %s,
      %s,
      %s
    """
    for index, event in enumerate(events, start=1):
        cursor.execute(
            statement,
            (
                json.dumps(event, sort_keys=True),
                "generated://streamflow_events.jsonl",
                index,
                "streamflow.events",
                "local_demo",
            ),
        )
        if index % 50 == 0:
            print(f"Inserted {index} Bronze rows", flush=True)


def print_results(title: str, rows: Iterable[tuple]) -> None:
    print(f"\n== {title}")
    for row in rows:
        print(" | ".join(str(value) for value in row))


def main() -> int:
    args = build_parser().parse_args()
    if args.no_proxy:
        clear_proxy_environment()
    load_env_file(args.env_file)

    import snowflake.connector

    cache_dir = PROJECT_ROOT / ".cache"
    cache_dir.mkdir(exist_ok=True)
    sample_path = cache_dir / "streamflow_events.jsonl"
    print(f"Generating {args.count} sample events at {sample_path}", flush=True)
    events = generate_sample(
        sample_path, count=args.count, seed=args.seed, invalid_rate=args.invalid_rate
    )

    with snowflake.connector.connect(**connection_kwargs()) as conn:
        with conn.cursor() as cursor:
            print("Connected to Snowflake", flush=True)
            run_setup(cursor)
            if args.reset_demo:
                print("Resetting demo tables", flush=True)
                reset_demo_tables(cursor)
            if args.load_mode == "stage":
                print("Uploading sample file to Snowflake stage", flush=True)
                stage_sample_file(cursor, sample_path)
                transform_files = TRANSFORM_FILES
            else:
                print("Inserting generated events into Bronze", flush=True)
                insert_bronze_events(cursor, events)
                transform_files = [
                    path for path in TRANSFORM_FILES if path != "sql/bronze/load_bronze_events.sql"
                ]

            collected_results: list[tuple[str, list[tuple]]] = []
            for relative_path in transform_files:
                collected_results.extend(execute_sql_file(cursor, relative_path))

            for title, rows in collected_results:
                print_results(title, rows)

            count_rows = cursor.execute(
                """
                SELECT 'bronze' AS layer, COUNT(*) FROM STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW
                UNION ALL
                SELECT 'silver_valid', COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
                UNION ALL
                SELECT 'silver_rejected', COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS
                UNION ALL
                SELECT 'gold_fact', COUNT(*) FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
                """
            ).fetchall()
            print_results("layer_counts", count_rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
