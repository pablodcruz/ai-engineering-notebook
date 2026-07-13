# Senior Review Guide

Use this guide to review the notebook as an engineering portfolio, not as a course outline.

## What To Inspect First

1. Run the workspace validation command:

   ```bash
   python scripts/validate_workspace.py
   ```

2. Review the runnable projects:

   - [Agentic Workflow Demo](../03-projects/agentic-workflow-demo.md)
   - [Prompt Regression Runner](../03-projects/prompt-regression-runner.md)
   - [Support Triage Review Console](../03-projects/live-support-triage-studio.md)
   - [Enablement Assistant RAG](../03-projects/enablement-assistant-rag.md)
   - [Local AI Lab Runner](../03-projects/local-ai-lab-runner.md)

3. Review the deployable showcase:

   - [Static showcase app](../docs/index.html)
   - [Agentic Workflow trace viewer](../docs/agentic-workflow.html)
   - [Prompt Regression comparison report](../docs/prompt-regression-report.html)
   - [Review Feedback candidate report](../docs/feedback-candidate-report.html)
   - [Mocked support adapter traces](../docs/support-adapter.html)
   - [Support Triage Review Console](../docs/support-triage.html)
   - [Enablement Assistant demo](../docs/enablement-assistant.html)
   - [Enablement Assistant eval report](../docs/enablement-eval-report.html)
   - [StreamFlow analytics dashboard](../docs/streamflow-dashboard.html)
   - [Deployment notes](../docs/DEPLOYMENT.md)

4. Review the operational thinking:

   - [Debugging Playbook](../04-explainers/debugging-playbook.md)
   - [Production Readiness Checklist](../04-explainers/production-readiness-checklist.md)
   - [AI Application Operating Economics](../04-explainers/ai-app-operating-economics.md)
   - [Evaluation And Observability](../01-concepts/evaluation-observability.md)
   - [AI System Review Checklist](../05-reference/ai-system-review-checklist.md)

## Review Rubric

| Area | Strong Signal | Where It Shows Up |
| --- | --- | --- |
| Agent safety | Tool permissions, approval gates, loop limits, and refusals are application-enforced | Agentic Workflow Demo |
| Observability | Decisions, tool calls, results, approvals, sources, and final states are traceable | Agent trace viewer |
| Grounding | Answers cite source paths and refuse uncovered questions | Enablement Assistant RAG |
| Evaluation | Balanced cases check retrieval, evidence-bearing citations, answer traits, partial coverage, adversarial requests, and refusal | RAG evals, eval report, and workspace validator |
| Prompt regression | Fixed inputs compare prompt candidates on schema, task correctness, grounding, and actionability | Prompt Regression Runner and comparison report |
| Human oversight | Model suggestions remain separate from accepted or corrected decisions, and override reasons become versioned synthetic evaluation evidence | Support Triage Review Console |
| Feedback governance | Corrections become deduplicated candidates, explicit approval is recorded, and permanent eval promotion remains a separate reviewed change | Review Feedback Pipeline |
| Customer integration | Signed events, strict mapping, replay protection, PII redaction, and proposed-only writes make the external-system boundary visible | Mocked Zendesk-Style Support Adapter |
| Cost control | Recorded/live separation, sample allowlisting, a global ceiling, a kill switch, and self-deployment make inference economics explicit | Support Triage Review Console and operating-economics explainer |
| Enablement | Technical behavior is translated into layered explanations, a timed session, failure demos, and customer workshop prompts | Prompt evaluation facilitator guide |
| Deployed product surface | Static demos expose core behavior without secrets or runtime services | Showcase app, RAG demo, StreamFlow dashboard |
| Developer experience | Local failures are diagnosed before model behavior is blamed | Local AI Lab Runner |
| Operability | Failure modes, setup paths, and troubleshooting are documented | Labs and explainers |
| Safety | Tool boundaries, credential handling, and refusal behavior are explicit | Agent lab, API lab, RAG project |
| Maintainability | One-command validation, pinned lint and type checks, branch-aware coverage, isolated browser tests, link checks, and CI make regressions visible | `scripts/validate_workspace.py`, `scripts/run_quality.py`, `QUALITY.md`, `BROWSER_TESTING.md`, and GitHub Actions |
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
