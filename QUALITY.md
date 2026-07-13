# Engineering Quality Automation

This repository has one root quality layer shared by the runnable Python projects. It complements behavioral tests and AI evaluations; it does not replace them.

## Commands

Run the dependency-light functional baseline:

```powershell
python scripts/validate_workspace.py
```

Install the pinned development tools and run the complete CI-equivalent gate:

```powershell
python -m pip install -r requirements-dev.txt
python scripts/validate_workspace.py --quality
```

Apply formatting intentionally before rerunning the gate:

```powershell
python -m ruff check . --fix
python -m ruff format .
```

## What The Quality Gate Checks

| Check | Scope | Evidence |
| --- | --- | --- |
| Ruff lint | First-party Python, excluding external framework adapters and fixtures | Correctness rules, imports, and modernization compatible with Python 3.10 |
| Ruff format | Same first-party Python scope | Deterministic formatting |
| mypy | Reusable domain and application-service modules | Typed interfaces and internal data flow |
| coverage.py | Deterministic business logic exercised by seven unit-test suites and three behavioral eval commands | Branch-aware terminal, XML, and HTML reports |

Tool versions are pinned in `requirements-dev.txt`. Configuration lives in root-level `ruff.toml`, `mypy.ini`, and `.coveragerc` files, so local and CI checks use the same rules without presenting quality metadata as an installable root Python application.

## Deliberate Boundaries

Strict typing initially covers reusable business logic rather than every adapter. The excluded files include:

- CLI argument-parsing entry points.
- Vercel `BaseHTTPRequestHandler` shims.
- Optional OpenAI live-recording code.
- Kafka, Spark, Airflow, and Snowflake integration adapters requiring external runtime packages or stubs. The dependency-free mocked support adapter core remains typed.
- Tests, fixtures, generated JSON, recorded outputs, prompts, and static web assets.

These boundaries are visible and narrow. They prevent missing third-party stubs from hiding actionable type errors in the core modules. Future milestones can type the adapters when their runtime dependencies become part of the validated environment.

## Coverage Policy

Coverage reports only the deterministic core represented by the unit-test suites. It excludes CLI wiring and external provider or platform adapters. The branch-aware floor is 80%.

Coverage is diagnostic evidence, not a claim about model quality. Prompt behavior, retrieval grounding, tool safety, and human-review behavior remain protected by their dedicated evals and contract tests.

Generated coverage files are written under `coverage/`, ignored by Git, and uploaded by GitHub Actions as the `python-coverage` artifact.
