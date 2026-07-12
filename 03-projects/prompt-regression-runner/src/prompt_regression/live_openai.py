from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from .contract import OUTPUT_SCHEMA


def build_request(prompt: str, ticket: str, model: str) -> dict[str, Any]:
    return {
        "model": model,
        "instructions": prompt,
        "input": ticket,
        "max_output_tokens": 300,
        "store": False,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "support_ticket_triage",
                "strict": True,
                "schema": OUTPUT_SCHEMA,
            }
        },
    }


def record_live_outputs(
    cases: list[dict[str, Any]],
    *,
    candidate: str,
    prompt_file: Path,
    model: str,
    output_path: Path,
) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the live extra with: pip install -e .[live]") from exc

    prompt = prompt_file.read_text(encoding="utf-8")
    client = OpenAI()
    outputs = []
    for case in cases:
        started = perf_counter()
        response = client.responses.create(**build_request(prompt, str(case["ticket"]), model))
        elapsed_ms = round((perf_counter() - started) * 1000, 2)
        outputs.append(
            {
                "case_id": case["id"],
                "output": json.loads(response.output_text),
                "latency_ms": elapsed_ms,
                "response_id": response.id,
            }
        )

    payload = {
        "candidate": candidate,
        "prompt_file": prompt_file.as_posix(),
        "source": "openai-responses-api",
        "model": model,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "outputs": outputs,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
