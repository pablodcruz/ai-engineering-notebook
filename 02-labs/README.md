# Labs

Labs are the heart of this workspace. Each lab should be small, repeatable, and easy to troubleshoot.

## Lab Standards

Every lab should include:

- Learning objectives.
- Skill level.
- Prerequisites.
- Setup steps.
- Exercise steps.
- Expected output.
- Common failure modes.
- Build notes.
- Debrief questions.

## Recommended Lab Sequence

1. Prompt engineering for structured outputs.
2. API or SDK first call.
3. RAG over a small document set.
4. Agent with one or two safe tools.
5. Troubleshooting challenge lab.

## Current Labs

| Lab | Focus | Credential required | Validation path |
| --- | --- | --- | --- |
| [Prompt Engineering](prompt-engineering-lab.md) | Structured output and iterative prompt improvement | No | Local known-good sample |
| [API And SDK Integration](api-sdk-integration-lab.md) | Environment setup, first provider call, and error diagnosis | Optional for readiness; real call requires a key | Readiness contract |
| [RAG](rag-lab.md) | Retrieval, grounding, citations, and refusal | No | Local known-good sample |
| [Agents Tool Use](agents-tool-use-lab.md) | Narrow tools, approval, traces, and prohibited actions | No | Local known-good sample |
| [Troubleshooting Drills](troubleshooting-drills.md) | Layered diagnosis across runtime and AI behavior | No | Local known-good sample |

## Run A Readiness Check

From the repository root:

```powershell
cd 03-projects/local-ai-lab-runner
$env:PYTHONPATH = "src"
python -m local_ai_lab_runner.cli check ../../02-labs/rag-lab.md
```

Run every repository check with:

```powershell
python scripts/validate_workspace.py
```

The [lab template](lab-template.md) intentionally contains placeholders. It is scaffolding for a new lab, not an incomplete published exercise.
