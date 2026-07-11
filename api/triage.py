from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import hmac
import json
import os

from api._triage_service import (
    OpenAIProvider,
    ServiceConfig,
    SlidingWindowRateLimiter,
    TriageService,
    UpstashDailyCounter,
    error_payload,
    get_live_sample,
    live_configuration_status,
    log_provider_failure,
)


RATE_LIMITER = SlidingWindowRateLimiter(
    limit=int(os.getenv("TRIAGE_RATE_LIMIT", "8")) if os.getenv("TRIAGE_RATE_LIMIT", "8").isdigit() else 8,
    window_seconds=60,
)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_common_headers()
        self.end_headers()

    def do_POST(self) -> None:
        request_id = "triage_gateway"
        if not live_configuration_status()["live_enabled"]:
            self._json(
                503,
                error_payload(request_id, "live_disabled", "Live model calls are currently disabled."),
            )
            return
        try:
            config = ServiceConfig.from_environment()
        except RuntimeError as exc:
            self._json(503, error_payload(request_id, "service_unconfigured", str(exc)))
            return

        client_key = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if not RATE_LIMITER.allow(client_key):
            self._json(429, error_payload(request_id, "rate_limited", "Too many demo requests. Retry in one minute."))
            return

        supplied = self.headers.get("X-Demo-Access-Code", "")
        if not hmac.compare_digest(supplied, config.access_code):
            self._json(401, error_payload(request_id, "access_denied", "A valid demo access code is required."))
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 12_000:
                raise ValueError("request body size is invalid")
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, error_payload(request_id, "invalid_json", str(exc)))
            return

        sample = get_live_sample(payload.get("sample_id"))
        if sample is None:
            self._json(
                400,
                error_payload(
                    request_id,
                    "invalid_sample",
                    "Live mode accepts only one of the published synthetic sample ids.",
                ),
            )
            return

        counter = UpstashDailyCounter(
            config.redis_url,
            config.redis_token,
            config.daily_limit,
        )
        try:
            claim = counter.claim()
        except Exception as exc:
            log_provider_failure(exc, request_id=request_id, stage="initialization")
            self._json(
                503,
                error_payload(
                    request_id,
                    "spend_guard_unavailable",
                    "The shared spend guard is unavailable, so the live request was stopped.",
                ),
            )
            return
        if not claim.allowed:
            response = error_payload(
                request_id,
                "daily_limit_reached",
                "The live-demo daily limit has been reached. The recorded walkthrough remains available.",
            )
            response["budget"] = {
                "daily_limit": claim.limit,
                "resets_at": claim.resets_at,
            }
            self._json(429, response)
            return

        try:
            provider = OpenAIProvider(config.model)
        except Exception:
            self._json(
                503,
                error_payload(
                    request_id,
                    "provider_unavailable",
                    "The model provider is not available. Check the deployment configuration.",
                ),
            )
            return

        service = TriageService(provider, model=config.model)
        status, response = service.run(sample["ticket"])
        if status == 200:
            response["telemetry"].update(
                {
                    "sample_id": sample["id"],
                    "daily_requests_used": claim.used,
                    "daily_limit": claim.limit,
                    "daily_limit_resets_at": claim.resets_at,
                }
            )
        self._json(status, response)

    def log_message(self, format: str, *args) -> None:
        # Avoid framework access logs containing user-supplied request bodies.
        return

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self) -> None:
        origin = os.getenv("TRIAGE_ALLOWED_ORIGIN", "null")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Demo-Access-Code")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
