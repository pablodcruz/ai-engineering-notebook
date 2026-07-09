CREATE SCHEMA IF NOT EXISTS STREAMFLOW_DB.GOLD;

CREATE TABLE IF NOT EXISTS STREAMFLOW_DB.GOLD.DIM_DATE (
  date_key NUMBER NOT NULL,
  date_day DATE NOT NULL,
  year_number NUMBER NOT NULL,
  month_number NUMBER NOT NULL,
  month_name STRING NOT NULL,
  week_number NUMBER NOT NULL,
  day_of_week_number NUMBER NOT NULL,
  day_name STRING NOT NULL,
  is_weekend BOOLEAN NOT NULL,
  CONSTRAINT pk_dim_date PRIMARY KEY (date_key)
);

CREATE TABLE IF NOT EXISTS STREAMFLOW_DB.GOLD.DIM_EVENT_TYPE (
  event_type STRING NOT NULL,
  event_group STRING NOT NULL,
  event_description STRING NOT NULL,
  CONSTRAINT pk_dim_event_type PRIMARY KEY (event_type)
);

CREATE TABLE IF NOT EXISTS STREAMFLOW_DB.GOLD.DIM_ENTITY (
  entity_id STRING NOT NULL,
  first_event_ts TIMESTAMP_NTZ NOT NULL,
  last_event_ts TIMESTAMP_NTZ NOT NULL,
  first_source STRING,
  total_events NUMBER NOT NULL,
  CONSTRAINT pk_dim_entity PRIMARY KEY (entity_id)
);

CREATE TABLE IF NOT EXISTS STREAMFLOW_DB.GOLD.FACT_EVENTS (
  event_key NUMBER AUTOINCREMENT,
  event_id STRING NOT NULL,
  entity_id STRING,
  event_type STRING NOT NULL,
  date_key NUMBER NOT NULL,
  event_date DATE NOT NULL,
  event_ts TIMESTAMP_NTZ NOT NULL,
  source STRING NOT NULL,
  amount NUMBER(18, 2),
  currency STRING,
  page STRING,
  ingest_run_id STRING NOT NULL,
  transformed_at TIMESTAMP_NTZ NOT NULL,
  CONSTRAINT pk_fact_events PRIMARY KEY (event_key)
);

CREATE TABLE IF NOT EXISTS STREAMFLOW_DB.GOLD.FACT_COMMERCE_METRICS (
  metric_date DATE NOT NULL,
  source STRING NOT NULL,
  event_type STRING NOT NULL,
  event_count NUMBER NOT NULL,
  distinct_entities NUMBER NOT NULL,
  total_amount NUMBER(18, 2) NOT NULL,
  average_amount NUMBER(18, 2),
  updated_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
