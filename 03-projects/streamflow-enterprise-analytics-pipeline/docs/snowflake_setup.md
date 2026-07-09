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

Run `sql/admin/bootstrap_streamflow.sql` in a Snowflake worksheet as an admin-capable role such as `ACCOUNTADMIN` for a trial account.

Replace the placeholder password before running:

```sql
CREATE USER IF NOT EXISTS STREAMFLOW_AGENT
  PASSWORD = '<replace-locally-before-running>'
  ...
```

Use a password you generate yourself and store locally. The next hardening step is key-pair authentication.

## Local Environment Variables

Option A: in PowerShell, set these in your current terminal:

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

Option B: create an ignored local env file:

```powershell
Copy-Item config\snowflake.env.example .env.snowflake
notepad .env.snowflake
```

Fill in the values locally. Do not commit `.env.snowflake`.

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

Or, if you used `.env.snowflake`:

```powershell
python scripts\snowflake_smoke_test.py --env-file .env.snowflake
```

If your terminal has a local proxy variable that blocks direct Snowflake access, use:

```powershell
python scripts\snowflake_smoke_test.py --env-file .env.snowflake --no-proxy
```

## Run The Demo Pipeline

After the smoke test passes, run a small end-to-end warehouse load:

```powershell
python scripts\run_snowflake_pipeline.py --env-file .env.snowflake --no-proxy --reset-demo
```

The default demo path generates synthetic Phase 1 events, inserts them into Bronze, transforms Silver, builds Gold, and prints quality/reconciliation checks. This avoids the local `PUT` upload path, which can be slower and more environment-sensitive.

To exercise the Snowflake internal stage path explicitly:

```powershell
python scripts\run_snowflake_pipeline.py --env-file .env.snowflake --no-proxy --reset-demo --load-mode stage
```

Export the latest Gold-layer metrics into the deployed static dashboard data file:

```powershell
python scripts\export_dashboard_data.py --env-file .env.snowflake --no-proxy
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
