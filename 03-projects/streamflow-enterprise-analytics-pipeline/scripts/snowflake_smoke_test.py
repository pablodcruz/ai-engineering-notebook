from __future__ import annotations

import os
import sys


REQUIRED_ENV = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
)


def env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def connection_kwargs() -> dict[str, str]:
    missing = [name for name in REQUIRED_ENV if not env(name)]
    authenticator = env("SNOWFLAKE_AUTHENTICATOR")
    password = env("SNOWFLAKE_PASSWORD")

    if not authenticator and not password:
        missing.append("SNOWFLAKE_PASSWORD or SNOWFLAKE_AUTHENTICATOR")

    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")

    kwargs = {
        "account": env("SNOWFLAKE_ACCOUNT"),
        "user": env("SNOWFLAKE_USER"),
        "role": env("SNOWFLAKE_ROLE"),
        "warehouse": env("SNOWFLAKE_WAREHOUSE"),
        "database": env("SNOWFLAKE_DATABASE"),
        "schema": env("SNOWFLAKE_SCHEMA", "BRONZE"),
    }
    if authenticator:
        kwargs["authenticator"] = authenticator
    else:
        kwargs["password"] = password
    return {key: value for key, value in kwargs.items() if value}


def main() -> int:
    try:
        import snowflake.connector
    except ImportError:
        print('Install the optional dependency first: python -m pip install -e ".[snowflake]"', file=sys.stderr)
        return 2

    try:
        with snowflake.connector.connect(**connection_kwargs()) as conn:
            with conn.cursor() as cur:
                row = cur.execute(
                    """
                    SELECT
                      CURRENT_ACCOUNT(),
                      CURRENT_USER(),
                      CURRENT_ROLE(),
                      CURRENT_WAREHOUSE(),
                      CURRENT_DATABASE(),
                      CURRENT_SCHEMA()
                    """
                ).fetchone()
    except Exception as exc:
        print(f"Snowflake connection failed: {exc}", file=sys.stderr)
        return 1

    labels = ("account", "user", "role", "warehouse", "database", "schema")
    print("Snowflake connection OK")
    for label, value in zip(labels, row):
        print(f"{label}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
