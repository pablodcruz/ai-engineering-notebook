from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import io
import json
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api._triage_service import (
    ServiceConfig,
    SlidingWindowRateLimiter,
    TriageService,
    UpstashDailyCounter,
    get_live_sample,
    log_provider_failure,
    validate_ticket,
)


VALID_OUTPUT = {
    "customer_problem": "Password reset email is missing",
    "product_area": "authentication",
    "urgency": "high",
    "missing_information": ["account email"],
    "recommended_response": "Confirm the account email and inspect reset delivery telemetry.",
}


class FakeProvider:
    def __init__(self, output=None, *, fail: bool = False) -> None:
        self.output = output if output is not None else VALID_OUTPUT
        self.fail = fail
        self.received = []

    def generate(self, ticket: str):
        self.received.append(ticket)
        if self.fail:
            raise RuntimeError("provider unavailable")
        return {
            "output": self.output,
            "response_id": "resp_test",
            "input_tokens": 42,
            "output_tokens": 21,
        }


class FakeResponse:
    def __init__(self, payload) -> None:
        self.buffer = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self.buffer

    def __exit__(self, exc_type, exc, traceback):
        self.buffer.close()


class LiveTriageServiceTests(unittest.TestCase):
    def test_service_config_requires_explicit_model(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_MODEL"):
                ServiceConfig.from_environment()

        with patch.dict(
            "os.environ",
            {
                "OPENAI_MODEL": "approved-model",
                "OPENAI_API_KEY": "provider-secret",
                "TRIAGE_DEMO_ACCESS_CODE": "demo-only",
                "UPSTASH_REDIS_REST_URL": "https://counter.example",
                "UPSTASH_REDIS_REST_TOKEN": "counter-secret",
                "TRIAGE_DAILY_LIMIT": "25",
                "TRIAGE_ALLOWED_ORIGIN": "https://demo.example",
            },
            clear=True,
        ):
            config = ServiceConfig.from_environment()
        self.assertEqual(config.model, "approved-model")
        self.assertEqual(config.access_code, "demo-only")
        self.assertEqual(config.daily_limit, 25)
        self.assertEqual(config.allowed_origin, "https://demo.example")

    def test_success_returns_validated_result_and_telemetry(self) -> None:
        provider = FakeProvider()
        service = TriageService(provider, model="test-model")

        status, payload = service.run("Reset email never arrives and I am locked out.")

        self.assertEqual(status, 200)
        self.assertEqual(payload["mode"], "live")
        self.assertTrue(payload["validation"]["passed"])
        self.assertEqual(payload["telemetry"]["model"], "test-model")
        self.assertEqual(payload["telemetry"]["prompt_version"], "structured-v2")
        self.assertFalse(payload["telemetry"]["stored_by_app"])
        self.assertEqual(len(provider.received), 1)

    def test_short_and_oversized_tickets_are_rejected_before_provider(self) -> None:
        provider = FakeProvider()
        service = TriageService(provider, model="test-model")

        short_status, _ = service.run("too short")
        long_status, _ = service.run("x" * 1001)

        self.assertEqual(short_status, 400)
        self.assertEqual(long_status, 400)
        self.assertEqual(provider.received, [])

    def test_provider_schema_failure_is_visible(self) -> None:
        service = TriageService(FakeProvider({"customer_problem": "Incomplete"}), model="test-model")

        status, payload = service.run("The customer supplied a sufficiently long ticket.")

        self.assertEqual(status, 502)
        self.assertEqual(payload["error"]["code"], "provider_contract_error")
        self.assertFalse(payload["validation"]["passed"])

    def test_provider_failure_does_not_expose_internal_exception(self) -> None:
        service = TriageService(FakeProvider(fail=True), model="test-model")

        with patch("builtins.print") as print_mock:
            status, payload = service.run("The customer supplied a sufficiently long ticket.")

        self.assertEqual(status, 502)
        self.assertEqual(payload["error"]["code"], "provider_error")
        self.assertNotIn("provider unavailable", str(payload))
        logged = json.loads(print_mock.call_args.args[0])
        self.assertEqual(logged["event"], "support_triage_provider_failure")
        self.assertEqual(logged["exception_type"], "RuntimeError")
        self.assertNotIn("provider unavailable", print_mock.call_args.args[0])

    def test_provider_log_includes_only_safe_correlation_fields(self) -> None:
        class FakeStatusError(Exception):
            status_code = 429
            request_id = "req_safe"
            code = "rate_limit_exceeded"

        with patch("builtins.print") as print_mock:
            log_provider_failure(FakeStatusError("secret message"), request_id="triage_safe", stage="generation")

        logged = json.loads(print_mock.call_args.args[0])
        self.assertEqual(logged["provider_http_status"], 429)
        self.assertEqual(logged["provider_request_id"], "req_safe")
        self.assertEqual(logged["provider_error_code"], "rate_limit_exceeded")
        self.assertNotIn("secret message", print_mock.call_args.args[0])

    def test_rate_limiter_resets_after_window(self) -> None:
        limiter = SlidingWindowRateLimiter(limit=2, window_seconds=10)

        self.assertTrue(limiter.allow("client", now=0))
        self.assertTrue(limiter.allow("client", now=1))
        self.assertFalse(limiter.allow("client", now=2))
        self.assertTrue(limiter.allow("client", now=12))

    def test_ticket_contract_is_explainable(self) -> None:
        self.assertIn("at least", validate_ticket("short") or "")
        self.assertIsNone(validate_ticket("A clear support issue with enough detail."))

    def test_live_samples_are_allowlisted_and_loaded_server_side(self) -> None:
        sample = get_live_sample("T001")

        self.assertIsNotNone(sample)
        self.assertIn("password", sample["ticket"].lower())
        self.assertIsNone(get_live_sample("T004"))
        self.assertIsNone(get_live_sample("not-a-sample"))

    def test_shared_daily_counter_returns_atomic_claim(self) -> None:
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers["Authorization"]
            captured["commands"] = json.loads(request.data)
            captured["timeout"] = timeout
            return FakeResponse([{"result": 3}, {"result": 1}])

        counter = UpstashDailyCounter(
            "https://counter.example/",
            "secret-token",
            3,
            opener=opener,
        )
        claim = counter.claim(now=datetime(2026, 7, 11, 12, tzinfo=timezone.utc))

        self.assertTrue(claim.allowed)
        self.assertEqual(claim.used, 3)
        self.assertEqual(claim.resets_at, "2026-07-12T00:00:00Z")
        self.assertEqual(captured["url"], "https://counter.example/multi-exec")
        self.assertEqual(captured["authorization"], "Bearer secret-token")
        self.assertEqual(captured["commands"][0][0], "INCR")

    def test_shared_daily_counter_denies_over_limit(self) -> None:
        counter = UpstashDailyCounter(
            "https://counter.example",
            "secret-token",
            3,
            opener=lambda request, timeout: FakeResponse([{"result": 4}, {"result": 1}]),
        )

        claim = counter.claim(now=datetime(2026, 7, 11, 12, tzinfo=timezone.utc))

        self.assertFalse(claim.allowed)
        self.assertEqual(claim.limit, 3)


if __name__ == "__main__":
    unittest.main()
