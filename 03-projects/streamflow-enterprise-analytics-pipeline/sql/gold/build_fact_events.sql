MERGE INTO STREAMFLOW_DB.GOLD.FACT_EVENTS target
USING (
  SELECT
    event_id,
    entity_id,
    event_type,
    TO_NUMBER(TO_CHAR(event_date, 'YYYYMMDD')) AS date_key,
    event_date,
    event_ts,
    source,
    amount,
    currency,
    page,
    ingest_run_id,
    transformed_at
  FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
) source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET
  entity_id = source.entity_id,
  event_type = source.event_type,
  date_key = source.date_key,
  event_date = source.event_date,
  event_ts = source.event_ts,
  source = source.source,
  amount = source.amount,
  currency = source.currency,
  page = source.page,
  ingest_run_id = source.ingest_run_id,
  transformed_at = source.transformed_at
WHEN NOT MATCHED THEN INSERT (
  event_id,
  entity_id,
  event_type,
  date_key,
  event_date,
  event_ts,
  source,
  amount,
  currency,
  page,
  ingest_run_id,
  transformed_at
)
VALUES (
  source.event_id,
  source.entity_id,
  source.event_type,
  source.date_key,
  source.event_date,
  source.event_ts,
  source.source,
  source.amount,
  source.currency,
  source.page,
  source.ingest_run_id,
  source.transformed_at
);
