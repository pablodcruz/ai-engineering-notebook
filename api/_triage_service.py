from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from time import perf_counter, time
from typing import Any, Protocol
from urllib.request import Request, urlopen
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
RUNNER_SRC = ROOT / "03-projects" / "prompt-regression-runner" / "src"
if str(RUNNER_SRC) not in sys.path:
    sys.path.insert(0, str(RUNNER_SRC))

from prompt_regression.contract import validate_output  # noqa: E402
from prompt_regression.live_openai import build_request  # noqa: E402


PROMPT_VERSION = "structured-v2"
PROMPT_PATH = ROOT / "03-projects" / "prompt-regression-runner" / "prompts" / f"{PROMPT_VERSION}.md"
CASES_PATH = ROOT / "03-projects" / "prompt-regression-runner" / "data" / "cases.jsonl"
LIVE_SAMPLE_IDS = ("T001", "T002", "T003")
MAX_TICKET_CHARS = 1_000


class Provider(Protocol):
    def generate(self, ticket: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ServiceConfig:
    model: str
    access_code: str
    redis_url: str
    redis_token: str
    daily_limit: int
    allowed_origin: str

    @classmethod
    def from_environment(cls) -> "ServiceConfig":
        model = os.getenv("OPENAI_MODEL", "").strip()
        access_code = os.getenv("TRIAGE_DEMO_ACCESS_CODE", "").strip()
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL", "").strip()
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip()
        allowed_origin = os.getenv("TRIAGE_ALLOWED_ORIGIN", "").strip()
        if not model:
            raise RuntimeError("OPENAI_MODEL is not configured")
        if not os.getenv("OPENAI_API_KEY", "").strip():
            raise RuntimeError("OPENAI_API_KEY is not configured")
        if not access_code:
            raise RuntimeError("TRIAGE_DEMO_ACCESS_CODE is not configured")
        if not redis_url or not redis_token:
            raise RuntimeError("the shared daily spend guard is not configured")
        if not allowed_origin or allowed_origin == "*":
            raise RuntimeError("TRIAGE_ALLOWED_ORIGIN must be a specific origin")
        try:
            daily_limit = int(os.getenv("TRIAGE_DAILY_LIMIT", "100"))
        except ValueError as exc:
            raise RuntimeError("TRIAGE_DAILY_LIMIT must be an integer") from exc
        if daily_limit < 1:
            raise RuntimeError("TRIAGE_DAILY_LIMIT must be positive")
        return cls(
            model=model,
            access_code=access_code,
            redis_url=redis_url.rstrip("/"),
            redis_token=redis_token,
            daily_limit=daily_limit,
            allowed_origin=allowed_origin,
        )


class OpenAIProvider:
    def __init__(self, model: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The OpenAI SDK is not installed") from exc
        self.model = model
        self.client = OpenAI()
        self.prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def generate(self, ticket: str) -> dict[str, Any]:
        response = self.client.responses.create(**build_request(self.prompt, ticket, self.model))
        usage = getattr(response, "usage", None)
        return {
            "output": json.loads(response.output_text),
            "response_id": response.id,
            "provider_request_id": getattr(response, "_request_id", None),
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }


class TriageService:
    def __init__(self, provider: Provider, *, model: str) -> None:
        self.provider = provider
        self.model = model

    def run(self, ticket: object) -> tuple[int, dict[str, Any]]:
        request_id = f"triage_{uuid4().hex[:12]}"
        validation_error = validate_ticket(ticket)
        if validation_error:
            return 400, error_payload(request_id, "invalid_request", validation_error)

        started = perf_counter()
        try:
            generated = self.provider.generate(str(ticket).strip())
        except Exception as exc:
            log_provider_failure(exc, request_id=request_id, stage="generation")
            return 502, error_payload(
                request_id,
                "provider_error",
                "The model provider could not complete this request. Try a recorded example or retry later.",
            )
        latency_ms = round((perf_counter() - started) * 1000, 2)
        output = generated.get("output")
        schema_errors = validate_output(output)
        if schema_errors:
            return 502, {
                **error_payload(
                    request_id,
                    "provider_contract_error",
                    "The model response did not satisfy the support-triage contract.",
                ),
                "validation": {"passed": False, "errors": schema_errors},
            }

        return 200, {
            "status": "ok",
            "mode": "live",
            "request_id": request_id,
            "result": output,
            "validation": {"passed": True, "errors": []},
            "telemetry": {
                "model": self.model,
                "prompt_version": PROMPT_VERSION,
                "latency_ms": latency_ms,
                "input_tokens": generated.get("input_tokens"),
                "output_tokens": generated.get("output_tokens"),
                "provider_response_id": generated.get("response_id"),
                "provider_request_id": generated.get("provider_request_id"),
                "stored_by_app": False,
            },
        }


class SlidingWindowRateLimiter:
    """Best-effort per-instance limiter; production needs a shared durable store."""

    def __init__(self, limit: int = 8, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def allow(self, key: str, *, now: float | None = None) -> bool:
        current = time() if now is None else now
        cutoff = current - self.window_seconds
        recent = [timestamp for timestamp in self._requests.get(key, []) if timestamp > cutoff]
        if len(recent) >= self.limit:
            self._requests[key] = recent
            return False
        recent.append(current)
        self._requests[key] = recent
        return True


@dataclass(frozen=True)
class DailyClaim:
    allowed: bool
    used: int
    limit: int
    resets_at: str


class UpstashDailyCounter:
    """Atomic, shared UTC-day request ceiling for serverless deployments."""

    def __init__(
        self,
        url: str,
        token: str,
        limit: int,
        *,
        opener=urlopen,
    ) -> None:
        self.url = url.rstrip("/")
        self.token = token
        self.limit = limit
        self.opener = opener

    def claim(self, *, now: datetime | None = None) -> DailyClaim:
        current = now or datetime.now(timezone.utc)
        current = current.astimezone(timezone.utc)
        day = current.strftime("%Y-%m-%d")
        key = f"support-triage:live-requests:{day}"
        commands = [["INCR", key], ["EXPIRE", key, 172800]]
        request = Request(
            f"{self.url}/multi-exec",
            data=json.dumps(commands).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with self.opener(request, timeout=5) as response:
            payload = json.load(response)
        if not isinstance(payload, list) or not payload or "result" not in payload[0]:
            raise RuntimeError("shared counter returned an invalid response")
        used = int(payload[0]["result"])
        tomorrow = datetime.fromtimestamp(
            (int(current.timestamp()) // 86400 + 1) * 86400,
            tz=timezone.utc,
        )
        return DailyClaim(
            allowed=used <= self.limit,
            used=used,
            limit=self.limit,
            resets_at=tomorrow.isoformat().replace("+00:00", "Z"),
        )


def get_live_sample(sample_id: object) -> dict[str, Any] | None:
    if not isinstance(sample_id, str) or sample_id not in LIVE_SAMPLE_IDS:
        return None
    for line in CASES_PATH.read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        if case.get("id") == sample_id:
            return case
    return None


def live_configuration_status() -> dict[str, bool]:
    try:
        daily_limit_valid = int(os.getenv("TRIAGE_DAILY_LIMIT", "100")) > 0
    except ValueError:
        daily_limit_valid = False
    return {
        "live_enabled": os.getenv("TRIAGE_LIVE_ENABLED", "").strip().lower() == "true",
        "model_configured": bool(os.getenv("OPENAI_MODEL", "").strip()),
        "provider_key_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "access_code_configured": bool(os.getenv("TRIAGE_DEMO_ACCESS_CODE", "").strip()),
        "daily_limit_configured": daily_limit_valid,
        "allowed_origin_configured": os.getenv("TRIAGE_ALLOWED_ORIGIN", "").strip() not in {"", "*"},
        "daily_guard_configured": bool(
            os.getenv("UPSTASH_REDIS_REST_URL", "").strip()
            and os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip()
        ),
    }


def validate_ticket(ticket: object) -> str | None:
    if not isinstance(ticket, str):
        return "ticket must be a string"
    stripped = ticket.strip()
    if len(stripped) < 12:
        return "ticket must contain at least 12 characters"
    if len(stripped) > MAX_TICKET_CHARS:
        return f"ticket must not exceed {MAX_TICKET_CHARS} characters"
    return None


def error_payload(request_id: str, code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "request_id": request_id, "error": {"code": code, "message": message}}


def log_provider_failure(exc: Exception, *, request_id: str, stage: str) -> None:
    """Emit correlation-safe provider diagnostics without prompts, tickets, or secrets."""
    event: dict[str, Any] = {
        "event": "support_triage_provider_failure",
        "request_id": request_id,
        "stage": stage,
        "exception_type": type(exc).__name__,
    }
    status_code = getattr(exc, "status_code", None)
    provider_request_id = getattr(exc, "request_id", None)
    error_code = getattr(exc, "code", None)
    if isinstance(status_code, int):
        event["provider_http_status"] = status_code
    if isinstance(provider_request_id, str) and provider_request_id:
        event["provider_request_id"] = provider_request_id
    if isinstance(error_code, str) and error_code:
        event["provider_error_code"] = error_code
    print(json.dumps(event, sort_keys=True), flush=True)
