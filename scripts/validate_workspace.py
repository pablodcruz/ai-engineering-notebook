from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks = [
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
    for name, command, cwd, extra_env in checks:
        print(f"\n== {name}")
        env = os.environ.copy()
        env.update(extra_env)
        result = subprocess.run(command, cwd=cwd, env=env, text=True)
        if result.returncode != 0:
            failures += 1
            print(f"FAILED: {name} exited {result.returncode}")

    if failures:
        print(f"\n{failures} workspace validation check(s) failed.")
        return 1

    print("\nAll workspace validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
