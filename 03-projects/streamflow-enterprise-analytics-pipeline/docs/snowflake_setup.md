# Snowflake Setup

This project can connect to Snowflake from your local terminal, but credentials must stay local. Do not paste passwords into chat and do not commit them to Git.

## What Snowflake Does Here

Snowflake is the warehouse for StreamFlow Phase 2:

```text
Phase 1 files
  -> Bronze raw events
  -> Silver cleaned events and rejected rows
  -> Gold facts and dimensions
  -> Power BI or static dashboard metrics
```

## Recommended Access Pattern

Use a dedicated role and user for this project instead of using a broad admin account.

Run this in a Snowflake worksheet as an admin-capable role such as `ACCOUNTADMIN` for a trial account:

```sql
USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS STREAMFLOW_ROLE;

CREATE WAREHOUSE IF NOT EXISTS STREAMFLOW_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS STREAMFLOW_DB;

GRANT USAGE ON WAREHOUSE STREAMFLOW_WH TO ROLE STREAMFLOW_ROLE;
GRANT USAGE ON DATABASE STREAMFLOW_DB TO ROLE STREAMFLOW_ROLE;
GRANT CREATE SCHEMA ON DATABASE STREAMFLOW_DB TO ROLE STREAMFLOW_ROLE;

CREATE USER IF NOT EXISTS STREAMFLOW_AGENT
  PASSWORD = '<create-a-strong-temporary-password-locally>'
  DEFAULT_ROLE = STREAMFLOW_ROLE
  DEFAULT_WAREHOUSE = STREAMFLOW_WH
  DEFAULT_NAMESPACE = STREAMFLOW_DB.BRONZE
  MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE STREAMFLOW_ROLE TO USER STREAMFLOW_AGENT;
```

Use a password you generate yourself and store locally. The next hardening step is key-pair authentication.

## Local Environment Variables

In PowerShell, set these in your current terminal:

```powershell
$env:SNOWFLAKE_ACCOUNT='your_account_identifier'
$env:SNOWFLAKE_USER='STREAMFLOW_AGENT'
$env:SNOWFLAKE_PASSWORD='your_local_password'
$env:SNOWFLAKE_ROLE='STREAMFLOW_ROLE'
$env:SNOWFLAKE_WAREHOUSE='STREAMFLOW_WH'
$env:SNOWFLAKE_DATABASE='STREAMFLOW_DB'
$env:SNOWFLAKE_SCHEMA='BRONZE'
```

The account identifier does not include `.snowflakecomputing.com`.

## Smoke Test

Install the optional connector:

```powershell
cd 03-projects\streamflow-enterprise-analytics-pipeline
python -m pip install -e ".[snowflake]"
```

Verify the connection:

```powershell
python scripts\snowflake_smoke_test.py
```

Expected output:

```text
Snowflake connection OK
account: ...
user: STREAMFLOW_AGENT
role: STREAMFLOW_ROLE
warehouse: STREAMFLOW_WH
database: STREAMFLOW_DB
schema: BRONZE
```

## Notes

- If your account requires MFA for password connections, use browser-based authentication for your own user or move to key-pair authentication for the service user.
- Keep the warehouse `XSMALL` and `AUTO_SUSPEND = 60` to control cost.
- The public website does not connect to Snowflake. It remains static and safe to share.
