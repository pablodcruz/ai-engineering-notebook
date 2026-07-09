# StreamFlow Dashboard Requirements

## Pages

### Executive Summary

- KPI cards: Total Events, Distinct Entities, Purchase Events, Purchase Rate, Revenue.
- Daily event trend by date.
- Event count by event type.
- Event count by source.

### Funnel And Commerce

- Add To Cart Events.
- Purchase Events.
- Cart To Purchase Rate.
- Revenue by source.
- Average Purchase Amount.

### Data Quality

- Bronze row count.
- Silver valid row count.
- Rejected row count by reason.
- Gold fact row count.
- Reconciliation status.

## Filters

- Date range.
- Source.
- Event type.
- Entity ID.

## QA Contract

Before demoing the dashboard:

1. Refresh the Power BI model.
2. Run `tests/reconciliation_checks.sql` in Snowflake.
3. Compare the Power BI Total Events card to `SELECT COUNT(*) FROM STREAMFLOW_DB.GOLD.FACT_EVENTS`.
4. Compare the Revenue card to the purchase revenue query in `powerbi/measures.md`.
5. Confirm slicers do not blank every visual unless the filtered segment is truly empty.

## Design Notes

- Use Gold tables only for the main report model.
- Keep rejected records in a separate data quality page, not mixed into business KPIs.
- Use clear measure names that match `powerbi/measures.md`.
- Avoid dashboard-only transformations for core KPIs; important business logic should live in Snowflake SQL or documented DAX.
