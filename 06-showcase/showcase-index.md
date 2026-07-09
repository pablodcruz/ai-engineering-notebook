# Showcase Index

Use this file to track artifacts that are polished enough to share.

## Candidate Artifacts

| Artifact | Status | What It Shows | Link |
| --- | --- | --- | --- |
| Prompt engineering lab | Demo-ready | Reliable structured-output design | ../02-labs/prompt-engineering-lab.md |
| RAG lab | Demo-ready | Grounded answer workflow and retrieval failure modes | ../02-labs/rag-lab.md |
| Debugging playbook | Drafted | Practical AI app troubleshooting | ../04-explainers/debugging-playbook.md |
| Enablement Assistant RAG | Runnable | RAG app architecture, source traceability, and evals | ../03-projects/enablement-assistant-rag.md |
| Local AI Lab Runner | Runnable | Developer experience, readiness checks, and reproducible experiments | ../03-projects/local-ai-lab-runner.md |

## Demo-Ready Commands

```bash
python scripts/validate_workspace.py
cd 03-projects/enablement-assistant && PYTHONPATH=src python -m enablement_assistant.cli eval
cd 03-projects/local-ai-lab-runner && PYTHONPATH=src python -m local_ai_lab_runner.cli run ../../02-labs/rag-lab.md
```

## Reviewer Signal

- The workspace has a single validation command.
- Runnable projects include tests and evals.
- Labs share a readiness contract and can be checked by the local runner.
- Project writeups explain architecture, limitations, troubleshooting, and demo paths.

## Polish Checklist

- Clear problem statement.
- Runnable or demoable path.
- Screenshots, logs, or sample output where useful.
- Failure modes documented.
- Practical takeaway included.
- No secrets or private context.
