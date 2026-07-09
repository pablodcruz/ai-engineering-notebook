from __future__ import annotations

import re
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


class Phase2ContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            "README.md",
            "config/snowflake.example.yml",
            "airflow/dags/snowflake_pipeline.py",
            "sql/bronze/create_bronze_tables.sql",
            "sql/bronze/load_bronze_events.sql",
            "sql/bronze/load_bronze_events_from_parquet.sql",
            "sql/silver/create_silver_tables.sql",
            "sql/silver/transform_silver_events.sql",
            "sql/silver/quality_checks.sql",
            "sql/gold/create_gold_tables.sql",
            "sql/gold/build_dimensions.sql",
            "sql/gold/build_fact_events.sql",
            "sql/gold/build_domain_metrics.sql",
            "powerbi/measures.md",
            "docs/data_dictionary.md",
            "docs/dashboard_requirements.md",
            "tests/reconciliation_checks.sql",
        ]
        missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
        self.assertEqual([], missing)

    def test_bronze_preserves_raw_payload_and_load_metadata(self) -> None:
        sql = read("sql/bronze/create_bronze_tables.sql").upper()
        for token in ["RAW_PAYLOAD VARIANT", "SOURCE_FILE", "SOURCE_ROW_NUMBER", "INGEST_RUN_ID", "LOADED_AT"]:
            self.assertIn(token, sql)
        self.assertIn("CREATE STAGE IF NOT EXISTS", sql)
        self.assertIn("STREAMFLOW_PARQUET_FORMAT", sql)

    def test_silver_transform_deduplicates_and_rejects_bad_records(self) -> None:
        sql = read("sql/silver/transform_silver_events.sql").upper()
        for token in [
            "ROW_NUMBER() OVER",
            "PARTITION BY RAW_PAYLOAD:EVENT_ID::STRING",
            "SILVER_REJECTED_EVENTS",
            "MERGE INTO STREAMFLOW_DB.SILVER.SILVER_EVENTS",
            "WHEN MATCHED THEN UPDATE",
            "WHEN NOT MATCHED THEN INSERT",
        ]:
            self.assertIn(token, sql)
        for reason in ["MISSING_EVENT_ID", "INVALID_EVENT_TS", "INVALID_EVENT_TYPE", "DUPLICATE_EVENT_ID"]:
            self.assertIn(reason, sql)

    def test_gold_model_contains_fact_and_dimensions(self) -> None:
        sql = read("sql/gold/create_gold_tables.sql").upper()
        for table in ["DIM_DATE", "DIM_EVENT_TYPE", "DIM_ENTITY", "FACT_EVENTS", "FACT_COMMERCE_METRICS"]:
            self.assertRegex(sql, rf"CREATE TABLE IF NOT EXISTS .*{table}")

    def test_quality_and_reconciliation_checks_return_failed_rows(self) -> None:
        quality_sql = read("sql/silver/quality_checks.sql").upper()
        reconciliation_sql = read("tests/reconciliation_checks.sql").upper()
        combined = quality_sql + "\n" + reconciliation_sql
        self.assertGreaterEqual(len(re.findall(r"FAILED_ROWS", combined)), 5)
        self.assertIn("BRONZE_TO_SILVER_RECONCILIATION", combined)
        self.assertIn("FACT_EVENT_TYPE_JOIN_INTEGRITY", combined)
        self.assertIn("FACT_DATE_JOIN_INTEGRITY", combined)

    def test_powerbi_measures_are_documented(self) -> None:
        measures = read("powerbi/measures.md")
        for measure in [
            "Total Events",
            "Distinct Entities",
            "Purchase Events",
            "Purchase Rate",
            "Revenue",
        ]:
            self.assertIn(measure, measures)
        self.assertIn("Validation Queries", measures)


if __name__ == "__main__":
    unittest.main()
