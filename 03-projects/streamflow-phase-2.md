# StreamFlow Phase 2: Enterprise Analytics Pipeline

## Problem

Phase 1 proves that events can be produced, streamed, validated, and written to durable files. Phase 2 answers the next question: how does that operational event stream become trusted business insight?

This project models the downstream warehouse and BI layer:

```text
Phase 1 output -> Snowflake Bronze -> Silver -> Gold star schema -> Power BI
```

## Architecture

| Component | Role |
| --- | --- |
| Snowflake Bronze | Stores raw event payloads and load metadata for auditability. |
| Snowflake Silver | Parses, validates, types, deduplicates, and separates rejected records. |
| Snowflake Gold | Publishes facts and dimensions for reporting. |
| Airflow | Orchestrates the load and transformation sequence. |
| Power BI | Presents KPIs, trends, filters, and dashboard QA checks. |

## Repository Artifact

Implementation folder:

[streamflow-enterprise-analytics-pipeline](streamflow-enterprise-analytics-pipeline/README.md)

The project is separate from the Phase 1 folder because the responsibilities are different. Phase 1 owns runtime streaming infrastructure. Phase 2 owns warehouse modeling, SQL transformations, BI semantics, and analytics validation.

## Data Contract

Phase 2 inherits the Phase 1 event contract:

| Field | Meaning |
| --- | --- |
| `event_id` | Deduplication key. |
| `event_type` | One of `page_view`, `add_to_cart`, `purchase`, `video_play`. |
| `event_ts` | Source event timestamp. |
| `source` | One of `simulator`, `web`, `mobile`, `api`. |
| `entity_id` | User/device/account/session identifier when available. |
| `payload` | Domain object containing fields such as `amount`, `currency`, and `page`. |

## Senior-Engineer Signals

- The medallion layers have explicit responsibilities.
- Raw events are preserved before transformation.
- Silver is rerunnable through `MERGE` instead of naive append-only inserts.
- Rejected records are first-class data, not silent loss.
- Gold is modeled as facts and dimensions instead of dashboard-shaped flat files.
- Power BI measures include Snowflake validation queries.
- Local tests verify the project contract without requiring live Snowflake credentials.

## Demo Path

Baseline local check:

```bash
cd 03-projects/streamflow-enterprise-analytics-pipeline
python -m unittest discover -s tests
```

Workspace check:

```bash
python scripts/validate_workspace.py
```

Live warehouse demo:

1. Generate or ingest Phase 1 output.
2. Stage the output in Snowflake.
3. Run the Bronze, Silver, and Gold SQL scripts in order.
4. Run reconciliation checks.
5. Refresh the Power BI model using the documented DAX measures.

## Limitations

This is a production-grade prototype, not a managed warehouse deployment. It intentionally avoids committing credentials, Snowflake account-specific configuration, or opaque `.pbix` binaries. The natural production hardening path is dbt for transformations/tests/docs, Snowpipe or Streams/Tasks for incremental processing, and proper Airflow connection secret management.
