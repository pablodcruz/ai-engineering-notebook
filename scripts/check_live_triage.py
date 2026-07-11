from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a deployed Support Triage Studio health endpoint.")
    parser.add_argument("base_url", help="Deployment base URL, for example https://project.vercel.app")
    parser.add_argument("--expect-configured", action="store_true", help="Fail unless provider configuration is present.")
    args = parser.parse_args()

    url = f"{args.base_url.rstrip('/')}/api/health"
    request = Request(url, headers={"User-Agent": "ai-engineering-notebook-smoke-check"})
    try:
        with urlopen(request, timeout=15) as response:
            status = response.status
            payload = json.load(response)
    except HTTPError as exc:
        status = exc.code
        try:
            payload = json.load(exc)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"FAIL: {url} returned HTTP {status} without JSON")
            return 1
    except (URLError, TimeoutError) as exc:
        print(f"FAIL: could not reach {url}: {exc.reason if isinstance(exc, URLError) else exc}")
        return 1

    required = {
        "status",
        "service",
        "prompt_version",
        "live_sample_ids",
        "live_enabled",
        "model_configured",
        "provider_key_configured",
        "access_code_configured",
        "daily_limit_configured",
        "allowed_origin_configured",
        "daily_guard_configured",
    }
    missing = sorted(required - set(payload)) if isinstance(payload, dict) else sorted(required)
    if missing or payload.get("service") != "support-triage":
        print(f"FAIL: health contract mismatch; missing={missing}")
        return 1
    if args.expect_configured and (status != 200 or payload.get("status") != "ok"):
        print(f"FAIL: deployment is reachable but not configured (HTTP {status})")
        return 1

    print(
        "PASS: support-triage health "
        f"status={payload['status']} prompt={payload['prompt_version']} http={status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
