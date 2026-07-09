from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


REQUIRED_ENV = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Environment file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError(f"Invalid env file line: {raw_line!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate local Snowflake connectivity for StreamFlow Phase 2.")
    parser.add_argument("--env-file", type=Path, help="Optional local env file with SNOWFLAKE_* values.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.env_file:
        try:
            load_env_file(args.env_file)
        except Exception as exc:
            print(f"Could not load env file: {exc}", file=sys.stderr)
            return 2

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
