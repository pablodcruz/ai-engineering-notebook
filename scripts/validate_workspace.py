from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks = [
        (
            "documentation links",
            [sys.executable, "scripts/check_links.py"],
            ROOT,
            {},
        ),
        (
            "enablement eval export freshness",
            [sys.executable, "scripts/export_enablement_eval.py", "--check"],
            ROOT,
            {},
        ),
        (
            "local-ai-lab-runner tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            ROOT / "03-projects" / "local-ai-lab-runner",
            {},
        ),
        (
            "enablement-assistant tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            ROOT / "03-projects" / "enablement-assistant",
            {},
        ),
        (
            "enablement-assistant eval",
            [sys.executable, "-m", "enablement_assistant.cli", "eval"],
            ROOT / "03-projects" / "enablement-assistant",
            {"PYTHONPATH": "src"},
        ),
        (
            "streamflow phase 1 tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            ROOT / "03-projects" / "streamflow-containerized-stream-processing",
            {},
        ),
        (
            "streamflow phase 2 tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            ROOT / "03-projects" / "streamflow-enterprise-analytics-pipeline",
            {},
        ),
    ]

    lab_root = ROOT / "02-labs"
    runner_root = ROOT / "03-projects" / "local-ai-lab-runner"
    for lab_path in sorted(lab_root.glob("*.md")):
        if lab_path.name in {"README.md", "lab-template.md"}:
            continue
        env = {"PYTHONPATH": "src"}
        if lab_path.name == "api-sdk-integration-lab.md":
            env["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "dummy-local-readiness-check")
        checks.append(
            (
                f"lab readiness: {lab_path.name}",
                [sys.executable, "-m", "local_ai_lab_runner.cli", "check", str(lab_path)],
                runner_root,
                env,
            )
        )

    failures = 0
    started = time.monotonic()
    for name, command, cwd, extra_env in checks:
        print(f"\n== {name}")
        env = os.environ.copy()
        env.update(extra_env)
        check_started = time.monotonic()
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
        elapsed = time.monotonic() - check_started
        if result.stdout.strip():
            print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip())
        if result.returncode != 0:
            failures += 1
            print(f"FAILED: {name} exited {result.returncode}")
        else:
            print(f"OK: {name} ({elapsed:.2f}s)")

    if failures:
        print(f"\n{failures} workspace validation check(s) failed.")
        return 1

    total_elapsed = time.monotonic() - started
    print(f"\nAll workspace validation checks passed in {total_elapsed:.2f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
