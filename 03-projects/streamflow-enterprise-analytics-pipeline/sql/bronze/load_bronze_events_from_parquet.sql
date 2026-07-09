COPY INTO STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW (
  raw_payload,
  source_file,
  source_row_number,
  stream_topic,
  ingest_run_id
)
FROM (
  SELECT
    COALESCE(
      TRY_PARSE_JSON($1:raw_json::STRING),
      OBJECT_CONSTRUCT_KEEP_NULL(
        'event_id', $1:event_id::STRING,
        'event_type', $1:event_type::STRING,
        'event_ts', $1:event_ts::STRING,
        'source', $1:source::STRING,
        'entity_id', $1:entity_id::STRING,
        'payload', TRY_PARSE_JSON($1:payload_json::STRING)
      )
    ) AS raw_payload,
    METADATA$FILENAME AS source_file,
    METADATA$FILE_ROW_NUMBER AS source_row_number,
    'streamflow.events' AS stream_topic,
    'local_001' AS ingest_run_id
  FROM @STREAMFLOW_DB.BRONZE.STREAMFLOW_STAGE
)
FILE_FORMAT = (FORMAT_NAME = STREAMFLOW_DB.BRONZE.STREAMFLOW_PARQUET_FORMAT)
ON_ERROR = CONTINUE;
