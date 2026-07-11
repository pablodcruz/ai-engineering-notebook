# Senior Review Guide

Use this guide to review the notebook as an engineering portfolio, not as a course outline.

## What To Inspect First

1. Run the workspace validation command:

   ```bash
   python scripts/validate_workspace.py
   ```

2. Review the runnable projects:

   - [Agentic Workflow Demo](../03-projects/agentic-workflow-demo.md)
   - [Enablement Assistant RAG](../03-projects/enablement-assistant-rag.md)
   - [Local AI Lab Runner](../03-projects/local-ai-lab-runner.md)

3. Review the deployable showcase:

   - [Static showcase app](../docs/index.html)
   - [Agentic Workflow trace viewer](../docs/agentic-workflow.html)
   - [Enablement Assistant demo](../docs/enablement-assistant.html)
   - [Enablement Assistant eval report](../docs/enablement-eval-report.html)
   - [StreamFlow analytics dashboard](../docs/streamflow-dashboard.html)
   - [Deployment notes](../docs/DEPLOYMENT.md)

4. Review the operational thinking:

   - [Debugging Playbook](../04-explainers/debugging-playbook.md)
   - [Production Readiness Checklist](../04-explainers/production-readiness-checklist.md)

## Review Rubric

| Area | Strong Signal | Where It Shows Up |
| --- | --- | --- |
| Agent safety | Tool permissions, approval gates, loop limits, and refusals are application-enforced | Agentic Workflow Demo |
| Observability | Decisions, tool calls, results, approvals, sources, and final states are traceable | Agent trace viewer |
| Grounding | Answers cite source paths and refuse uncovered questions | Enablement Assistant RAG |
| Evaluation | Balanced cases check retrieval, evidence-bearing citations, answer traits, partial coverage, adversarial requests, and refusal | RAG evals, eval report, and workspace validator |
| Deployed product surface | Static demos expose core behavior without secrets or runtime services | Showcase app, RAG demo, StreamFlow dashboard |
| Developer experience | Local failures are diagnosed before model behavior is blamed | Local AI Lab Runner |
| Operability | Failure modes, setup paths, and troubleshooting are documented | Labs and explainers |
| Safety | Tool boundaries, credential handling, and refusal behavior are explicit | Agent lab, API lab, RAG project |
| Maintainability | One-command validation, link checks, and CI make regressions visible | `scripts/validate_workspace.py`, `scripts/check_links.py`, and GitHub Actions |
| Communication | Each artifact explains problem, architecture, limitations, and demo path | Project writeups and showcase |

## Questions A Senior Engineer Should Ask

- What behavior is deterministic, and what would become model-dependent in production?
- Which failures are caught by tests, which are caught by evals, and which need human review?
- What is the smallest trusted baseline that proves the environment works?
- Where are secrets, source data, and generated artifacts kept out of version control?
- What would need authentication, authorization, observability, and cost controls before production?

## Current Intentional Boundaries

- No live model calls are required for baseline demos.
- No secrets are stored in the repo.
- Prototypes favor observable local behavior over hidden managed services.
- The static showcase is deployable, but GitHub Pages must be enabled from repository settings.
