# Local AI Lab Runner

A dependency-light CLI that checks whether local AI labs are ready to run. It validates lab markdown structure, inspects the Python environment, checks credential presence when a lab needs it, and prints clear troubleshooting guidance.

## Quick Start

PowerShell:

```powershell
cd 03-projects\local-ai-lab-runner
$env:PYTHONPATH='src'
python -m local_ai_lab_runner.cli list
python -m local_ai_lab_runner.cli check ..\..\02-labs\api-sdk-integration-lab.md
python -m local_ai_lab_runner.cli doctor
```

Bash or Git Bash:

```bash
cd 03-projects/local-ai-lab-runner
PYTHONPATH=src python -m local_ai_lab_runner.cli list
PYTHONPATH=src python -m local_ai_lab_runner.cli check ../../02-labs/api-sdk-integration-lab.md
PYTHONPATH=src python -m local_ai_lab_runner.cli doctor
```

Optional install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
ai-lab-runner list
```

## Demo Commands

```powershell
ai-lab-runner check ..\..\02-labs\api-sdk-integration-lab.md
ai-lab-runner check ..\..\02-labs\api-sdk-integration-lab.md --simulate missing-credential
ai-lab-runner check ..\..\02-labs\api-sdk-integration-lab.md --simulate missing-package
ai-lab-runner run ..\..\02-labs\rag-lab.md
ai-lab-runner sample
```

## What It Checks

- Lab file exists and is readable.
- Lab has a title and practical structure.
- Recommended lab sections are present.
- Python runtime meets the minimum version.
- Required packages can be imported.
- Required credential environment variables exist when applicable.
- A known-good local sample can run without network access.

## Prototype Boundary

This prototype does not execute arbitrary lab code. It is a readiness and checkpoint runner, not a task orchestrator. That is deliberate: the first production problem for local AI experiments is reducing avoidable setup uncertainty before model behavior enters the picture.
