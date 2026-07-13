from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_RUNNER_ROOT = Path(__file__).resolve().parents[3] / "prompt-regression-runner"
DEFAULT_RECORDING = PROMPT_RUNNER_ROOT / "recorded" / "structured-v2.json"


class RecordedTriageEngine:
    """Credential-free adapter over reviewed Prompt Regression Runner outputs."""

    def __init__(self, recording_path: Path = DEFAULT_RECORDING) -> None:
        payload = json.loads(recording_path.read_text(encoding="utf-8"))
        outputs = payload.get("outputs")
        if not isinstance(outputs, list):
            raise ValueError("Recorded triage fixture is invalid")
        self._outputs: dict[str, dict[str, Any]] = {}
        for item in outputs:
            if isinstance(item, dict) and isinstance(item.get("output"), dict):
                self._outputs[str(item.get("case_id"))] = item["output"]

    def triage(self, case_id: str, ticket: str) -> dict[str, Any]:
        del ticket
        if case_id not in self._outputs:
            raise ValueError(f"No recorded triage output for {case_id}")
        return dict(self._outputs[case_id])
