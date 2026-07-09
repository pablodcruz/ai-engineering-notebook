CREATE OR REPLACE TEMP TABLE STAGED_EVENTS AS
SELECT
  raw_payload:event_id::STRING AS event_id,
  raw_payload:event_type::STRING AS event_type,
  raw_payload:entity_id::STRING AS entity_id,
  TRY_TO_TIMESTAMP_NTZ(raw_payload:event_ts::STRING) AS event_ts,
  TO_DATE(TRY_TO_TIMESTAMP_NTZ(raw_payload:event_ts::STRING)) AS event_date,
  raw_payload:source::STRING AS source,
  TRY_TO_DECIMAL(raw_payload:payload.amount::STRING, 18, 2) AS amount,
  raw_payload:payload.currency::STRING AS currency,
  raw_payload:payload.page::STRING AS page,
  raw_payload:payload AS payload,
  stream_topic,
  ingest_run_id,
  source_file,
  loaded_at,
  CASE
    WHEN raw_payload:event_id IS NULL THEN 'missing_event_id'
    WHEN raw_payload:event_type IS NULL THEN 'missing_event_type'
    WHEN raw_payload:source IS NULL THEN 'missing_source'
    WHEN raw_payload:payload IS NULL THEN 'missing_payload'
    WHEN TRY_TO_TIMESTAMP_NTZ(raw_payload:event_ts::STRING) IS NULL THEN 'invalid_event_ts'
    WHEN raw_payload:event_type::STRING NOT IN ('page_view', 'add_to_cart', 'purchase', 'video_play') THEN 'invalid_event_type'
    WHEN raw_payload:source::STRING NOT IN ('simulator', 'web', 'mobile', 'api') THEN 'invalid_source'
    WHEN TYPEOF(raw_payload:payload) <> 'OBJECT' THEN 'invalid_payload'
    ELSE NULL
  END AS rejection_reason,
  ROW_NUMBER() OVER (
    PARTITION BY raw_payload:event_id::STRING
    ORDER BY loaded_at DESC, source_file DESC
  ) AS event_rank
FROM STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW;

INSERT INTO STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS (
  rejection_id,
  raw_payload,
  rejection_reason,
  source_file,
  stream_topic,
  ingest_run_id,
  loaded_at
)
SELECT
  SHA2(CONCAT_WS('|', COALESCE(event_id, 'missing'), COALESCE(source_file, 'unknown'), COALESCE(rejection_reason, 'duplicate')), 256),
  OBJECT_CONSTRUCT_KEEP_NULL(
    'event_id', event_id,
    'event_type', event_type,
    'entity_id', entity_id,
    'source', source,
    'payload', payload
  ),
  CASE WHEN event_rank > 1 THEN 'duplicate_event_id' ELSE rejection_reason END,
  source_file,
  stream_topic,
  ingest_run_id,
  loaded_at
FROM STAGED_EVENTS
WHERE rejection_reason IS NOT NULL
   OR event_rank > 1;

MERGE INTO STREAMFLOW_DB.SILVER.SILVER_EVENTS target
USING (
  SELECT *
  FROM STAGED_EVENTS
  WHERE rejection_reason IS NULL
    AND event_rank = 1
) source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET
  event_type = source.event_type,
  entity_id = source.entity_id,
  event_ts = source.event_ts,
  event_date = source.event_date,
  source = source.source,
  amount = source.amount,
  currency = source.currency,
  page = source.page,
  payload = source.payload,
  stream_topic = source.stream_topic,
  ingest_run_id = source.ingest_run_id,
  source_file = source.source_file,
  loaded_at = source.loaded_at,
  transformed_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
  event_id,
  event_type,
  entity_id,
  event_ts,
  event_date,
  source,
  amount,
  currency,
  page,
  payload,
  stream_topic,
  ingest_run_id,
  source_file,
  loaded_at
)
VALUES (
  source.event_id,
  source.event_type,
  source.entity_id,
  source.event_ts,
  source.event_date,
  source.source,
  source.amount,
  source.currency,
  source.page,
  source.payload,
  source.stream_topic,
  source.ingest_run_id,
  source.source_file,
  source.loaded_at
);
