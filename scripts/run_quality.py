from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MYPY_TARGETS = [
    "api/_triage_service.py",
    "03-projects/enablement-assistant/src/enablement_assistant/answer.py",
    "03-projects/enablement-assistant/src/enablement_assistant/documents.py",
    "03-projects/enablement-assistant/src/enablement_assistant/evaluation.py",
    "03-projects/enablement-assistant/src/enablement_assistant/retrieval.py",
    "03-projects/agentic-workflow-demo/src/agentic_workflow/backlog.py",
    "03-projects/agentic-workflow-demo/src/agentic_workflow/evals.py",
    "03-projects/agentic-workflow-demo/src/agentic_workflow/models.py",
    "03-projects/agentic-workflow-demo/src/agentic_workflow/tools.py",
    "03-projects/agentic-workflow-demo/src/agentic_workflow/workflow.py",
    "03-projects/local-ai-lab-runner/src/local_ai_lab_runner/checks.py",
    "03-projects/local-ai-lab-runner/src/local_ai_lab_runner/labs.py",
    "03-projects/local-ai-lab-runner/src/local_ai_lab_runner/runner.py",
    "03-projects/prompt-regression-runner/src/prompt_regression/contract.py",
    "03-projects/prompt-regression-runner/src/prompt_regression/dataset.py",
    "03-projects/prompt-regression-runner/src/prompt_regression/feedback.py",
    "03-projects/prompt-regression-runner/src/prompt_regression/scoring.py",
    "03-projects/streamflow-containerized-stream-processing/src/streamflow/quality.py",
    "03-projects/streamflow-containerized-stream-processing/src/streamflow/schemas.py",
]

COVERAGE_TEST_DIRS = [
    "tests",
    "03-projects/enablement-assistant/tests",
    "03-projects/agentic-workflow-demo/tests",
    "03-projects/local-ai-lab-runner/tests",
    "03-projects/prompt-regression-runner/tests",
    "03-projects/streamflow-containerized-stream-processing/tests",
]


def run(name: str, command: list[str], *, env: dict[str, str] | None = None) -> bool:
    print(f"\n== {name}", flush=True)
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, env=env)
    elapsed = time.monotonic() - started
    if result.returncode:
        print(f"FAILED: {name} exited {result.returncode}")
        return False
    print(f"OK: {name} ({elapsed:.2f}s)")
    return True


def main() -> int:
    checks = [
        ("ruff lint", [sys.executable, "-m", "ruff", "check", "."]),
        ("ruff format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
        ("mypy core modules", [sys.executable, "-m", "mypy", *MYPY_TARGETS]),
    ]
    for name, command in checks:
        if not run(name, command):
            return 1

    if not run("coverage reset", [sys.executable, "-m", "coverage", "erase"]):
        return 1
    for test_dir in COVERAGE_TEST_DIRS:
        if not run(
            f"coverage tests: {test_dir}",
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                "--parallel-mode",
                "-m",
                "unittest",
                "discover",
                "-s",
                test_dir,
            ],
        ):
            return 1

    eval_workloads = [
        (
            "coverage eval: enablement assistant",
            "03-projects/enablement-assistant/src",
            ["-m", "enablement_assistant.cli", "eval"],
        ),
        (
            "coverage eval: agentic workflow",
            "03-projects/agentic-workflow-demo/src",
            ["-m", "agentic_workflow.cli", "eval"],
        ),
        (
            "coverage eval: prompt regression",
            "03-projects/prompt-regression-runner/src",
            [
                "-m",
                "prompt_regression.cli",
                "--cases",
                "03-projects/prompt-regression-runner/data/cases.jsonl",
                "compare",
                "03-projects/prompt-regression-runner/recorded/baseline-v1.json",
                "03-projects/prompt-regression-runner/recorded/structured-v2.json",
            ],
        ),
    ]
    for name, python_path, arguments in eval_workloads:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / python_path)
        if not run(
            name,
            [sys.executable, "-m", "coverage", "run", "--parallel-mode", *arguments],
            env=env,
        ):
            return 1

    coverage_steps = [
        ("coverage combine", [sys.executable, "-m", "coverage", "combine"]),
        ("coverage report", [sys.executable, "-m", "coverage", "report"]),
        (
            "coverage XML artifact",
            [sys.executable, "-m", "coverage", "xml", "-o", "coverage/coverage.xml"],
        ),
        ("coverage HTML artifact", [sys.executable, "-m", "coverage", "html"]),
    ]
    for name, command in coverage_steps:
        if not run(name, command):
            return 1

    print("\nAll engineering quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
