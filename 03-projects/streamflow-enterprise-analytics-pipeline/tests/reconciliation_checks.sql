SELECT 'gold_fact_matches_silver' AS check_name,
  ABS(
    (SELECT COUNT(*) FROM STREAMFLOW_DB.SILVER.SILVER_EVENTS)
    - (SELECT COUNT(*) FROM STREAMFLOW_DB.GOLD.FACT_EVENTS)
  ) AS failed_rows;

SELECT 'fact_event_type_join_integrity' AS check_name, COUNT(*) AS failed_rows
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS fact
LEFT JOIN STREAMFLOW_DB.GOLD.DIM_EVENT_TYPE event_type
  ON fact.event_type = event_type.event_type
WHERE event_type.event_type IS NULL;

SELECT 'fact_date_join_integrity' AS check_name, COUNT(*) AS failed_rows
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS fact
LEFT JOIN STREAMFLOW_DB.GOLD.DIM_DATE date_dim
  ON fact.date_key = date_dim.date_key
WHERE date_dim.date_key IS NULL;

SELECT 'powerbi_total_events' AS metric_name, COUNT(*) AS metric_value
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS;

SELECT 'powerbi_purchase_revenue' AS metric_name, COALESCE(SUM(amount), 0) AS metric_value
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
WHERE event_type = 'purchase';
