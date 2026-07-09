SELECT 'silver_required_fields' AS check_name, COUNT(*) AS failed_rows
FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
WHERE event_id IS NULL
   OR event_type IS NULL
   OR event_ts IS NULL
   OR event_date IS NULL
   OR source IS NULL
   OR payload IS NULL;

SELECT 'silver_duplicate_event_id' AS check_name, COUNT(*) AS failed_rows
FROM (
  SELECT event_id
  FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
  GROUP BY event_id
  HAVING COUNT(*) > 1
);

SELECT 'silver_accepted_event_types' AS check_name, COUNT(*) AS failed_rows
FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
WHERE event_type NOT IN ('page_view', 'add_to_cart', 'purchase', 'video_play');

SELECT 'silver_accepted_sources' AS check_name, COUNT(*) AS failed_rows
FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
WHERE source NOT IN ('simulator', 'web', 'mobile', 'api');

SELECT 'bronze_to_silver_reconciliation' AS check_name,
  ABS(
    (SELECT COUNT(*) FROM STREAMFLOW_DB.BRONZE.BRONZE_EVENTS_RAW)
    - (
      (SELECT COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS)
      + (SELECT COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_REJECTED_EVENTS)
    )
  ) AS failed_rows;
