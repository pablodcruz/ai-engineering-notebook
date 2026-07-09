CREATE OR REPLACE TABLE STREAMFLOW_DB.GOLD.FACT_COMMERCE_METRICS AS
SELECT
  event_date AS metric_date,
  source,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT entity_id) AS distinct_entities,
  COALESCE(SUM(CASE WHEN event_type IN ('purchase', 'add_to_cart') THEN amount ELSE 0 END), 0) AS total_amount,
  AVG(CASE WHEN event_type IN ('purchase', 'add_to_cart') THEN amount END) AS average_amount,
  CURRENT_TIMESTAMP() AS updated_at
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
GROUP BY event_date, source, event_type;
