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
| StreamFlow Phase 1 | Scaffolded | Streaming data platform design, Spark jobs, Airflow orchestration, and data quality | ../03-projects/streamflow-phase-1.md |
| StreamFlow Phase 2 | Scaffolded | Snowflake medallion modeling, BI semantic layer, Airflow orchestration, and reconciliation checks | ../03-projects/streamflow-phase-2.md |

## Demo-Ready Commands

```bash
python scripts/validate_workspace.py
cd 03-projects/enablement-assistant && PYTHONPATH=src python -m enablement_assistant.cli eval
cd 03-projects/local-ai-lab-runner && PYTHONPATH=src python -m local_ai_lab_runner.cli run ../../02-labs/rag-lab.md
```

## Deployable Showcase

The static showcase app lives at [../docs/index.html](../docs/index.html). It presents the strongest project evidence, lab maturity, and validation path for senior-engineer review.

StreamFlow has a deployed project report at [../docs/streamflow-report.html](../docs/streamflow-report.html).

StreamFlow Phase 2 has a deployed analytics report at [../docs/streamflow-analytics-report.html](../docs/streamflow-analytics-report.html).

## Reviewer Signal

- The workspace has a single validation command.
- Runnable projects include tests and evals.
- Labs share a readiness contract and can be checked by the local runner.
- Project writeups explain architecture, limitations, troubleshooting, and demo paths.
- [Senior Review Guide](../00-meta/senior-review-guide.md) names the strongest engineering signals.
- [Production Readiness Checklist](../04-explainers/production-readiness-checklist.md) frames what would need to change before production.

## Polish Checklist

- Clear problem statement.
- Runnable or demoable path.
- Screenshots, logs, or sample output where useful.
- Failure modes documented.
- Practical takeaway included.
- No secrets or private context.
