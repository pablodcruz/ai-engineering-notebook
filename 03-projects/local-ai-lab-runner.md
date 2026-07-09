# Project: Local AI Lab Runner

## Problem

AI experiments often fail before the interesting part: missing credentials, mismatched runtimes, unavailable packages, wrong endpoints, or unclear setup steps. A local lab runner makes those failures visible before a learner starts changing prompts, model settings, or application code.

## Audience

AI engineers, technical trainers, workshop facilitators, and learners running local notebook labs.

## Why This Matters

Good enablement tooling separates environment failure from model behavior. A known-good readiness path gives debugging a baseline and helps learners spend their time on the experiment itself.

## Architecture

```text
Markdown lab files
  -> lab discovery
  -> markdown structure parser
  -> readiness checks
  -> checkpoint plan
  -> PASS/WARN/FAIL report with fixes
```

### Components

| Component | Prototype Choice | Production Path |
| --- | --- | --- |
| Lab discovery | Scans `02-labs/*.md` | Workspace manifests and lab tags |
| Lab validation | Required and recommended markdown headings | Schema-backed lab metadata |
| Runtime checks | Python version and import checks | Language-specific toolchain adapters |
| Credential checks | Environment variable presence | Secret provider integration and scoped credentials |
| Known-good sample | Local deterministic sample | Provider-specific smoke requests behind explicit opt-in |
| Output | CLI text and JSON | CI annotations, workshop dashboards, and logs |

## Implementation

Runnable prototype:

[03-projects/local-ai-lab-runner/README.md](local-ai-lab-runner/README.md)

Core behavior:

- Lists markdown labs.
- Checks lab file structure against the notebook lab standard.
- Validates local Python runtime.
- Confirms baseline package imports.
- Detects explicit credential requirements from lab text, such as `OPENAI_API_KEY`.
- Reports actionable `PASS`, `WARN`, and `FAIL` findings.
- Prints checkpoint steps for a lab run.
- Simulates common demo failures.

## Setup

Dependency-light path:

PowerShell:

```powershell
cd 03-projects\local-ai-lab-runner
$env:PYTHONPATH='src'
python -m local_ai_lab_runner.cli list
```

Bash or Git Bash:

```bash
cd 03-projects/local-ai-lab-runner
PYTHONPATH=src python -m local_ai_lab_runner.cli list
```

Optional install:

```powershell
cd 03-projects\local-ai-lab-runner
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
ai-lab-runner list
```

## Demo Script

1. List available labs:

   ```powershell
   ai-lab-runner list
   ```

2. Run environment-only checks:

   ```powershell
   ai-lab-runner doctor
   ```

3. Check a lab that needs credentials:

   ```powershell
   ai-lab-runner check ..\..\02-labs\api-sdk-integration-lab.md
   ```

4. Simulate a missing dependency:

   ```powershell
   ai-lab-runner check ..\..\02-labs\rag-lab.md --simulate missing-package
   ```

5. Show checkpoint guidance for a lab:

   ```powershell
   ai-lab-runner run ..\..\02-labs\rag-lab.md
   ```

6. Show machine-readable output:

   ```powershell
   ai-lab-runner run ..\..\02-labs\rag-lab.md --json
   ```

## Evaluation

Tests cover:

- Lab discovery.
- Markdown structure parsing.
- Passing readiness checks.
- Credential detection.
- Simulated missing package behavior.
- Checkpoint construction.

Manual verification commands:

```powershell
python -m unittest discover -s tests
$env:PYTHONPATH='src'; python -m local_ai_lab_runner.cli list
$env:PYTHONPATH='src'; python -m local_ai_lab_runner.cli run ..\..\02-labs\rag-lab.md --json
```

## Production Readiness Notes

What is prototype-grade:

- Heuristic credential detection.
- Python-only runtime checks.
- Local markdown lab discovery.
- No execution of arbitrary lab code.

What is production-shaped:

- Clear check result contract.
- Human-readable and JSON output.
- Failure simulation for demos and tests.
- Explicit checkpoint model.
- Dependency-free baseline.
- Exit codes suitable for automation.

## Known Limitations

- The runner does not execute lab exercises.
- It does not validate provider endpoints, quotas, or live network access.
- Credential checks only confirm presence, not validity.
- Lab section checks are heading-based and do not prove content quality.
- Package checks are static imports, not full dependency resolution.

## Troubleshooting

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| API lab fails credential check | `OPENAI_API_KEY` is not set in the active shell | Set the variable for the current terminal or run a non-API lab |
| Lab shows many warnings | The markdown lab is missing recommended sections | Add headings from `02-labs/README.md` or document why they are not needed |
| Package check fails | Dependency is not installed in the active environment | Activate the expected virtual environment and install the package |
| JSON output fails a consumer | Consumer expects different field names | Use the stable `severity`, `check`, `message`, and `fix` fields |

## Demo Talking Points

- Good experiments reduce avoidable uncertainty.
- Clear checkpoints separate environment failure from model behavior.
- A known-good path gives debugging a baseline.
- Warnings are useful because they improve lab quality without blocking exploration.
- Readiness tooling is part of developer experience, not administrative overhead.
