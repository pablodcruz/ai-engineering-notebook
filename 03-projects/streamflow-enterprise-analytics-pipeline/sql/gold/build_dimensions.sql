MERGE INTO STREAMFLOW_DB.GOLD.DIM_DATE target
USING (
  SELECT DISTINCT
    TO_NUMBER(TO_CHAR(event_date, 'YYYYMMDD')) AS date_key,
    event_date AS date_day,
    YEAR(event_date) AS year_number,
    MONTH(event_date) AS month_number,
    TO_CHAR(event_date, 'MMMM') AS month_name,
    WEEKOFYEAR(event_date) AS week_number,
    DAYOFWEEKISO(event_date) AS day_of_week_number,
    TO_CHAR(event_date, 'DY') AS day_name,
    DAYOFWEEKISO(event_date) IN (6, 7) AS is_weekend
  FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
) source
ON target.date_key = source.date_key
WHEN MATCHED THEN UPDATE SET
  date_day = source.date_day,
  year_number = source.year_number,
  month_number = source.month_number,
  month_name = source.month_name,
  week_number = source.week_number,
  day_of_week_number = source.day_of_week_number,
  day_name = source.day_name,
  is_weekend = source.is_weekend
WHEN NOT MATCHED THEN INSERT (
  date_key,
  date_day,
  year_number,
  month_number,
  month_name,
  week_number,
  day_of_week_number,
  day_name,
  is_weekend
)
VALUES (
  source.date_key,
  source.date_day,
  source.year_number,
  source.month_number,
  source.month_name,
  source.week_number,
  source.day_of_week_number,
  source.day_name,
  source.is_weekend
);

MERGE INTO STREAMFLOW_DB.GOLD.DIM_EVENT_TYPE target
USING (
  SELECT 'page_view' AS event_type, 'engagement' AS event_group, 'Page view event' AS event_description
  UNION ALL SELECT 'add_to_cart', 'commerce', 'Cart addition event'
  UNION ALL SELECT 'purchase', 'commerce', 'Completed purchase event'
  UNION ALL SELECT 'video_play', 'media', 'Video playback event'
) source
ON target.event_type = source.event_type
WHEN MATCHED THEN UPDATE SET
  event_group = source.event_group,
  event_description = source.event_description
WHEN NOT MATCHED THEN INSERT (event_type, event_group, event_description)
VALUES (source.event_type, source.event_group, source.event_description);

MERGE INTO STREAMFLOW_DB.GOLD.DIM_ENTITY target
USING (
  SELECT
    entity_id,
    MIN(event_ts) AS first_event_ts,
    MAX(event_ts) AS last_event_ts,
    MIN_BY(source, event_ts) AS first_source,
    COUNT(*) AS total_events
  FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS
  WHERE entity_id IS NOT NULL
  GROUP BY entity_id
) source
ON target.entity_id = source.entity_id
WHEN MATCHED THEN UPDATE SET
  first_event_ts = source.first_event_ts,
  last_event_ts = source.last_event_ts,
  first_source = source.first_source,
  total_events = source.total_events
WHEN NOT MATCHED THEN INSERT (
  entity_id,
  first_event_ts,
  last_event_ts,
  first_source,
  total_events
)
VALUES (
  source.entity_id,
  source.first_event_ts,
  source.last_event_ts,
  source.first_source,
  source.total_events
);
