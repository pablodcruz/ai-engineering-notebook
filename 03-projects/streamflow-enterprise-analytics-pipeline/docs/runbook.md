# StreamFlow Phase 2 Runbook

## Normal Batch Run

1. Confirm Phase 1 output exists and represents the demo window.
2. Upload the output files to `STREAMFLOW_DB.BRONZE.STREAMFLOW_STAGE`.
3. Run the Bronze load.
4. Run Silver transforms.
5. Run Silver quality checks.
6. Run Gold dimensions and facts.
7. Run reconciliation checks.
8. Refresh Power BI.

## Failure Modes

| Symptom | Likely Cause | Response |
| --- | --- | --- |
| Bronze row count is zero | Stage is empty or wrong file format | List stage files and confirm JSON/Parquet strategy. |
| Most rows are rejected | Event contract changed in Phase 1 | Compare `raw_payload` keys with Phase 1 `schemas.py`. |
| Duplicate count is high | Same files loaded under the same run strategy | Confirm stage cleanup, load history, and `event_id` uniqueness. |
| Power BI totals differ | Model is stale or visual filter is active | Refresh model and validate against Gold queries. |
| Snowflake cost grows unexpectedly | Warehouse left running or oversized | Use XSMALL, auto-suspend, and bounded demo loads. |

## Production Hardening Path

- Move SQL transformations to dbt models with sources, exposures, docs, and tests.
- Replace manual stage loads with Snowpipe where continuous ingestion is needed.
- Add Snowflake Streams and Tasks for incremental transformations.
- Use external secrets management for Airflow connections.
- Add role-based access controls separating Bronze raw access from Gold BI access.
