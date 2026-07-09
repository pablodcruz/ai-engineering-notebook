# StreamFlow Phase 2 Data Dictionary

## Bronze

### `BRONZE_EVENTS_RAW`

| Column | Type | Meaning |
| --- | --- | --- |
| `raw_payload` | `VARIANT` | Raw event object loaded from Phase 1 output. |
| `source_file` | `STRING` | Snowflake load metadata for the staged source file. |
| `source_row_number` | `NUMBER` | Row number inside the staged file. |
| `stream_topic` | `STRING` | Topic name that produced the event, usually `streamflow.events`. |
| `ingest_run_id` | `STRING` | Manual or scheduled load run identifier. |
| `loaded_at` | `TIMESTAMP_NTZ` | Warehouse load timestamp. |

## Silver

### `SILVER_EVENTS`

| Column | Type | Meaning |
| --- | --- | --- |
| `event_id` | `STRING` | Stable event identifier and deduplication key. |
| `event_type` | `STRING` | Accepted type: `page_view`, `add_to_cart`, `purchase`, or `video_play`. |
| `entity_id` | `STRING` | User, device, account, or session identifier. |
| `event_ts` | `TIMESTAMP_NTZ` | Parsed event timestamp. |
| `event_date` | `DATE` | Derived reporting date. |
| `source` | `STRING` | Accepted source: `simulator`, `web`, `mobile`, or `api`. |
| `amount` | `NUMBER(18,2)` | Payload amount for commerce events. |
| `currency` | `STRING` | Payload currency. |
| `page` | `STRING` | Payload page context. |
| `payload` | `VARIANT` | Original typed payload object. |
| `stream_topic` | `STRING` | Source topic metadata. |
| `ingest_run_id` | `STRING` | Load run metadata. |
| `source_file` | `STRING` | Original staged file. |
| `loaded_at` | `TIMESTAMP_NTZ` | Bronze load timestamp. |
| `transformed_at` | `TIMESTAMP_NTZ` | Silver transformation timestamp. |

### `SILVER_REJECTED_EVENTS`

Stores rows that failed required-field, timestamp, accepted-value, payload-shape, or duplicate checks.

## Gold

### `DIM_DATE`

Calendar attributes for trend reporting and slicers.

### `DIM_EVENT_TYPE`

Business grouping for event types:

| Event Type | Group |
| --- | --- |
| `page_view` | `engagement` |
| `add_to_cart` | `commerce` |
| `purchase` | `commerce` |
| `video_play` | `media` |

### `DIM_ENTITY`

One row per entity with first/last activity, first source, and total event count.

### `FACT_EVENTS`

One row per valid event. This is the primary Power BI fact table.

### `FACT_COMMERCE_METRICS`

Aggregated daily/source/event metrics for fast dashboard cards and trend checks.
