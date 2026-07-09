# StreamFlow Power BI Measures

Use these DAX measures against the Gold model.

Recommended model relationships:

| From | To | Cardinality |
| --- | --- | --- |
| `fact_events[date_key]` | `dim_date[date_key]` | Many to one |
| `fact_events[event_type]` | `dim_event_type[event_type]` | Many to one |
| `fact_events[entity_id]` | `dim_entity[entity_id]` | Many to one |

## Core Measures

```DAX
Total Events =
COUNTROWS(fact_events)
```

```DAX
Distinct Entities =
DISTINCTCOUNT(fact_events[entity_id])
```

```DAX
Purchase Events =
CALCULATE(
    [Total Events],
    fact_events[event_type] = "purchase"
)
```

```DAX
Add To Cart Events =
CALCULATE(
    [Total Events],
    fact_events[event_type] = "add_to_cart"
)
```

```DAX
Purchase Rate =
DIVIDE([Purchase Events], [Total Events])
```

```DAX
Cart To Purchase Rate =
DIVIDE([Purchase Events], [Add To Cart Events])
```

```DAX
Revenue =
CALCULATE(
    SUM(fact_events[amount]),
    fact_events[event_type] = "purchase"
)
```

```DAX
Average Purchase Amount =
CALCULATE(
    AVERAGE(fact_events[amount]),
    fact_events[event_type] = "purchase"
)
```

```DAX
Events Per Entity =
DIVIDE([Total Events], [Distinct Entities])
```

## Validation Queries

Run these in Snowflake and compare with Power BI visuals after refresh:

```sql
SELECT COUNT(*) AS total_events
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS;
```

```sql
SELECT COUNT(DISTINCT entity_id) AS distinct_entities
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS;
```

```sql
SELECT COALESCE(SUM(amount), 0) AS revenue
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
WHERE event_type = 'purchase';
```

```sql
SELECT event_date, event_type, source, COUNT(*) AS event_count
FROM STREAMFLOW_DB.GOLD.FACT_EVENTS
GROUP BY event_date, event_type, source
ORDER BY event_date, event_type, source;
```
