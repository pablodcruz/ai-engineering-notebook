from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
from typing import Any

from snowflake_smoke_test import clear_proxy_environment, connection_kwargs, load_env_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "streamflow-dashboard-data.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export public-safe StreamFlow dashboard data from Snowflake.")
    parser.add_argument("--env-file", type=Path, required=True, help="Local env file with SNOWFLAKE_* values.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Dashboard JSON output path.")
    parser.add_argument("--no-proxy", action="store_true", help="Clear proxy environment variables for this process.")
    return parser


def json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def fetch_dicts(cursor, sql: str) -> list[dict[str, Any]]:
    cursor.execute(sql)
    columns = [column[0].lower() for column in cursor.description]
    return [
        {column: json_value(value) for column, value in zip(columns, row)}
        for row in cursor.fetchall()
    ]


def main() -> int:
    args = build_parser().parse_args()
    if args.no_proxy:
        clear_proxy_environment()
    load_env_file(args.env_file)

    import snowflake.connector

    with snowflake.connector.connect(**connection_kwargs()) as conn:
        with conn.cursor() as cursor:
            raw_rows = fetch_dicts(
                cursor,
                """
                SELECT
                  event_date AS date,
                  source,
                  event_type AS eventType,
                  COUNT(*) AS events,
                  COUNT(DISTINCT entity_id) AS entities,
                  COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN amount ELSE 0 END), 0) AS revenue
                FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
                GROUP BY event_date, source, event_type
                ORDER BY event_date, source, event_type
                """,
            )
            rows = [
                {
                    "date": row["date"],
                    "source": row["source"],
                    "eventType": row.get("eventtype") or row.get("event_type"),
                    "events": row["events"],
                    "entities": row["entities"],
                    "revenue": row["revenue"],
                }
                for row in raw_rows
            ]
            rejected_rows = fetch_dicts(
                cursor,
                """
                SELECT
                  rejection_reason AS reason,
                  COUNT(*) AS count
                FROM STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS
                GROUP BY rejection_reason
                ORDER BY count DESC, rejection_reason
                """,
            )
            layer_counts = {
                row["layer"]: int(row["row_count"])
                for row in fetch_dicts(
                    cursor,
                    """
                    SELECT 'bronze' AS layer, COUNT(*) AS row_count FROM STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW
                    UNION ALL
                    SELECT 'silver_valid', COUNT(*) AS row_count FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
                    UNION ALL
                    SELECT 'silver_rejected', COUNT(*) AS row_count FROM STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS
                    UNION ALL
                    SELECT 'gold_fact', COUNT(*) AS row_count FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
                    """,
                )
            }
            checks = fetch_dicts(
                cursor,
                """
                SELECT 'gold_fact_matches_silver' AS check_name,
                  ABS(
                    (SELECT COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS)
                    - (SELECT COUNT(*) FROM STREAMFLOW_DB.GOLD.FACT_EVENTS)
                  ) AS failed_rows
                UNION ALL
                SELECT 'fact_event_type_join_integrity' AS check_name, COUNT(*) AS failed_rows
                FROM STREAMFLOW_DB.GOLD.FACT_EVENTS fact
                LEFT JOIN STREAMFLOW_DB.GOLD.DIM_EVENT_TYPE event_type
                  ON fact.event_type = event_type.event_type
                WHERE event_type.event_type IS NULL
                UNION ALL
                SELECT 'fact_date_join_integrity' AS check_name, COUNT(*) AS failed_rows
                FROM STREAMFLOW_DB.GOLD.FACT_EVENTS fact
                LEFT JOIN STREAMFLOW_DB.GOLD.DIM_DATE date_dim
                  ON fact.date_key = date_dim.date_key
                WHERE date_dim.date_key IS NULL
                """,
            )
            metadata = {
                "source": "snowflake",
                "exported_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            }

    payload = {
        "metadata": metadata,
        "rows": rows,
        "rejectedRows": rejected_rows,
        "layerCounts": layer_counts,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported dashboard data to {args.output}")
    print(f"Rows: {len(rows)}; rejected groups: {len(rejected_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
