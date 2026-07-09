# Project: StreamFlow Phase 1

## Problem

Streaming data platforms combine several moving parts: producers, Kafka-compatible brokers, Spark streaming jobs, durable storage, batch summaries, orchestration, logs, and data quality rules. A small but complete local platform makes those boundaries concrete without hiding behind managed services.

## Audience

Data engineers, AI engineers, and technical trainers who need to explain how event-driven data systems feed analytics, AI readiness, and downstream evaluation workflows.

## Why This Matters

Senior AI systems work often depends on upstream data quality. StreamFlow shows how event data becomes reliable enough to use: events are produced, ingested incrementally, checked, persisted, summarized, and orchestrated with clear outputs and failure modes.

## Architecture

```text
Synthetic event producer
  -> Redpanda Kafka-compatible topic
  -> Spark Structured Streaming ingest
  -> Raw valid Parquet + rejected records + checkpoint
  -> Spark batch summary job
  -> Airflow bounded orchestration and output validation
```

## Implementation

Runnable project:

[streamflow-containerized-stream-processing/README.md](streamflow-containerized-stream-processing/README.md)

Core artifacts:

- Producer: `src/streamflow/producer.py`
- Data contract and validation: `src/streamflow/schemas.py`, `src/streamflow/quality.py`
- Streaming ingest job: `spark/jobs/streaming_ingest.py`
- Batch summary job: `spark/jobs/daily_summary.py`
- Airflow DAG: `airflow/dags/streamflow_daily_summary.py`
- Docker Compose platform: `docker/compose.yml`

## Production-Shaped Improvements

The base requirements call for Kafka, Spark, Airflow, and Docker. This implementation adds a few senior-level improvements:

- A dependency-light local test path for schema and quality rules.
- Dry-run event generation so the data contract can be inspected without Kafka.
- Explicit rejected-record reasons.
- Parameterized runtime paths and broker settings.
- Bounded Airflow orchestration instead of trying to own an infinite streaming loop.
- A static project report for the deployed showcase.

## Demo Script

1. Generate local sample events:

   ```bash
   cd 03-projects/streamflow-containerized-stream-processing
   PYTHONPATH=src python -m streamflow.producer --dry-run --count 20 --out data/sample/events.jsonl
   ```

2. Run unit tests:

   ```bash
   python -m unittest discover -s tests
   ```

3. Start the local platform:

   ```bash
   docker compose -f docker/compose.yml up -d redpanda
   ```

4. Produce events to Redpanda:

   ```bash
   docker compose -f docker/compose.yml run --rm producer
   ```

5. Run streaming ingest with Spark:

   ```bash
   docker compose -f docker/compose.yml run --rm spark spark-submit spark/jobs/streaming_ingest.py
   ```

6. Trigger the bounded summary workflow in Airflow or run the summary job directly:

   ```bash
   docker compose -f docker/compose.yml run --rm spark spark-submit spark/jobs/daily_summary.py
   ```

## Evaluation

Baseline checks:

- Unit tests validate required-field checks, timestamp parsing, allowed values, duplicate detection, and reject reasons.
- The workspace validator runs the StreamFlow tests without requiring Docker.
- Manual platform checks verify Redpanda topic production, Spark checkpointing, Parquet outputs, and summary outputs.

## Known Limitations

- Docker-based Spark and Airflow smoke tests are manual, not part of CI.
- The local Spark job may download the Kafka connector package on first run.
- Redpanda is used as a Kafka-compatible broker to keep the local stack lighter.
- This phase uses local filesystem storage instead of object storage.
- The Airflow DAG coordinates bounded batch work; it does not supervise a long-running streaming service.

## Troubleshooting

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Producer cannot connect | Broker is not ready or wrong advertised listener | Check `docker compose ps`, Redpanda logs, and `STREAMFLOW_BROKER` |
| Spark cannot read Kafka | Missing Spark Kafka connector package | Use the documented `spark-submit --packages` command |
| No Parquet output appears | No events were produced or checkpoint reused old offsets | Produce fresh events or clear the local checkpoint intentionally |
| Airflow DAG imports fail | Python path or mounted volume is wrong | Confirm `/opt/streamflow` mount and DAG environment variables |
| Summary is empty | Ingest job wrote no valid records | Inspect reject output and producer logs |

## Demo Talking Points

- Streaming systems need durable boundaries between each component.
- Airflow is best used for bounded orchestration, not infinite stream ownership.
- Checkpointing is what lets Spark streaming resume safely.
- Rejected records are not a side effect; they are a required data product.
- Data quality is an AI-readiness concern, not just a data engineering concern.

