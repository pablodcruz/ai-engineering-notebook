COPY INTO STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW (
  raw_payload,
  source_file,
  source_row_number,
  stream_topic,
  ingest_run_id
)
FROM (
  SELECT
    $1 AS raw_payload,
    METADATA$FILENAME AS source_file,
    METADATA$FILE_ROW_NUMBER AS source_row_number,
    'streamflow.events' AS stream_topic,
    'local_001' AS ingest_run_id
  FROM @STREAMFLOW_DB.BRONZE.STREAMFLOW_STAGE
)
FILE_FORMAT = (FORMAT_NAME = STREAMFLOW_DB.BRONZE.STREAMFLOW_JSON_FORMAT)
ON_ERROR = CONTINUE;
