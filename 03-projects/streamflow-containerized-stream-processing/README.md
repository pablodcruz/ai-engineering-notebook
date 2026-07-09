# StreamFlow Phase 1

A containerized streaming data platform prototype using Redpanda, Spark Structured Streaming, Airflow, Docker Compose, and Python data quality logic.

## What It Builds

```text
Producer -> Redpanda topic -> Spark streaming ingest -> Parquet + checkpoint
                                              |
                                              v
                              Spark batch summary -> Airflow bounded workflow
```

## Quick Local Checks

Run these without Docker, Kafka, Spark, or Airflow:

```bash
cd 03-projects/streamflow-containerized-stream-processing
PYTHONPATH=src python -m streamflow.producer --dry-run --count 10 --out data/sample/events.jsonl
python -m unittest discover -s tests
```

## Full Platform Demo

Start Redpanda:

```bash
docker compose -f docker/compose.yml up -d redpanda
```

Produce synthetic events:

```bash
docker compose -f docker/compose.yml run --rm producer
```

Run Spark Structured Streaming ingest:

```bash
docker compose -f docker/compose.yml run --rm spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
  spark/jobs/streaming_ingest.py \
  --broker redpanda:9092 \
  --topic streamflow.events \
  --raw-output data/raw/events \
  --rejects-output data/rejects/events \
  --checkpoint data/checkpoints/events \
  --trigger availableNow
```

Run the bounded summary job:

```bash
docker compose -f docker/compose.yml run --rm spark spark-submit \
  spark/jobs/daily_summary.py \
  --input data/raw/events \
  --output data/curated/daily_summary
```

Start Airflow for the bounded workflow:

```bash
docker compose -f docker/compose.yml up airflow
```

Airflow UI:

```text
http://localhost:8080
```

Default local credentials are configured in `docker/compose.yml` for prototype use only.

For this local prototype, Airflow uses `SequentialExecutor` with SQLite so the orchestration layer stays small. A production-like deployment should use a metadata database such as Postgres and an executor appropriate for the workload.

## Configuration

Runtime values should come from CLI flags or environment variables:

| Setting | Default |
| --- | --- |
| `STREAMFLOW_BROKER` | `redpanda:9092` |
| `STREAMFLOW_TOPIC` | `streamflow.events` |
| `STREAMFLOW_RAW_OUTPUT` | `data/raw/events` |
| `STREAMFLOW_REJECTS_OUTPUT` | `data/rejects/events` |
| `STREAMFLOW_CHECKPOINT` | `data/checkpoints/events` |
| `STREAMFLOW_SUMMARY_OUTPUT` | `data/curated/daily_summary` |

## Data Contract

Required event fields:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `event_id` | string | yes | `evt_001` |
| `event_type` | string | yes | `purchase` |
| `event_ts` | timestamp string | yes | `2026-06-30T14:30:00Z` |
| `source` | string | yes | `simulator` |
| `payload` | object | yes | `{"amount": 19.99}` |
| `entity_id` | string | no | `user_123` |

Allowed event types:

- `page_view`
- `add_to_cart`
- `purchase`
- `video_play`

Allowed sources:

- `simulator`
- `web`
- `mobile`
- `api`

## Expected Outputs

| Output | Purpose |
| --- | --- |
| Redpanda topic | Kafka-compatible event buffer |
| `data/raw/events` | Valid parsed stream records as Parquet |
| `data/rejects/events` | Invalid records and rejection reasons |
| `data/checkpoints/events` | Spark streaming checkpoint |
| `data/curated/daily_summary` | Batch summary output |
| Airflow logs | Bounded orchestration history |

## Testing

```bash
python -m unittest discover -s tests
```

The unit tests focus on deterministic data quality behavior. Docker/Spark/Airflow checks are documented as manual smoke tests because they require local container runtime and connector downloads.

## Troubleshooting

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Producer connection fails | Redpanda is not ready | Wait for the healthcheck or inspect `docker compose logs redpanda` |
| Spark Kafka read fails | Connector package missing | Include the documented `--packages` argument |
| No valid output | Generated records were invalid or no events were produced | Inspect `data/rejects/events` and producer logs |
| Summary path missing | Ingest job has not written raw data | Run producer and streaming ingest first |
| Airflow cannot find jobs | Volume mount or working directory mismatch | Confirm `/opt/streamflow` mount in `docker/compose.yml` |
