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
| Agentic Workflow Demo | Runnable | Typed tools, approval boundaries, structured traces, refusal behavior, and behavioral evals | ../03-projects/agentic-workflow-demo.md |
| Prompt Regression Runner | Runnable | Prompt comparison, structured regression checks, recorded/live separation, and trainer facilitation | ../03-projects/prompt-regression-runner.md |
| Review Feedback Pipeline | Runnable | Strict synthetic-export validation, human-correction summaries, deduplicated candidate eval cases, and explicit approval boundaries | ../docs/feedback-candidate-report.html |
| Mocked Zendesk-Style Support Adapter | Runnable | Signed webhook verification, replay handling, PII redaction, replaceable mapping, and proposed-only external updates | ../docs/support-adapter.html |
| Support Triage Review Console | Live | Controlled synthetic model calls, human accept/correct decisions, review metrics, sanitized feedback export, layered cost controls, and safe self-deployment | ../03-projects/live-support-triage-studio.md |
| StreamFlow Phase 1 | Scaffolded | Streaming data platform design, Spark jobs, Airflow orchestration, and data quality | ../03-projects/streamflow-phase-1.md |
| StreamFlow Phase 2 | Scaffolded | Snowflake medallion modeling, BI semantic layer, Airflow orchestration, and reconciliation checks | ../03-projects/streamflow-phase-2.md |

## Demo-Ready Commands

```bash
python scripts/validate_workspace.py
cd 03-projects/enablement-assistant && PYTHONPATH=src python -m enablement_assistant.cli eval
cd 03-projects/local-ai-lab-runner && PYTHONPATH=src python -m local_ai_lab_runner.cli run ../../02-labs/rag-lab.md
cd 03-projects/agentic-workflow-demo && PYTHONPATH=src python -m agentic_workflow.cli eval
cd 03-projects/prompt-regression-runner && PYTHONPATH=src python -m prompt_regression.cli compare recorded/baseline-v1.json recorded/structured-v2.json
```

## Deployable Showcase

The static showcase app lives at [../docs/index.html](../docs/index.html). It presents the strongest project evidence, lab maturity, and validation path for senior-engineer review.

The Enablement Assistant has a deployed static demo at [../docs/enablement-assistant.html](../docs/enablement-assistant.html). It demonstrates grounded answers, citations, retrieved context, and refusal behavior without secrets or a runtime server.

The Enablement Assistant eval report lives at [../docs/enablement-eval-report.html](../docs/enablement-eval-report.html). It renders exported CLI eval results from [../docs/enablement-eval-data.json](../docs/enablement-eval-data.json).

The Agentic Workflow trace viewer lives at [../docs/agentic-workflow.html](../docs/agentic-workflow.html). It renders deterministic traces for read-only execution, approval checkpoints, approved simulations, and prohibited-action refusal.

The Prompt Regression report lives at [../docs/prompt-regression-report.html](../docs/prompt-regression-report.html). It compares two candidates across fixed support tickets and links aggregate scores to case-level failures.

The Feedback Candidate report lives at [../docs/feedback-candidate-report.html](../docs/feedback-candidate-report.html). It shows how sanitized human corrections become deduplicated, awaiting-review evaluation candidates without automatically changing the permanent golden set.

The Mocked Support Adapter trace viewer lives at [../docs/support-adapter.html](../docs/support-adapter.html). It demonstrates customer-system integration behavior across valid, redacted, duplicate, unauthenticated, and unsupported synthetic webhook deliveries without an external account or mutation.

The Support Triage Review Console lives at [../docs/support-triage.html](../docs/support-triage.html). It turns the same evaluated task into a customer-facing workflow, labels live and recorded execution separately, captures human accept/correct decisions, exports synthetic feedback, and exposes its cost controls. The [deploy-your-own guide](../docs/deploy-support-triage.html) keeps reviewer credentials and billing inside their own deployment.

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
