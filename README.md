# AI Engineering Notebook

[![Validate Workspace](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/validate.yml/badge.svg)](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/validate.yml)
[![Link Check](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/link-check.yml/badge.svg)](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/link-check.yml)
[![Deploy Showcase](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/deploy-showcase.yml/badge.svg)](https://github.com/pablodcruz/ai-engineering-notebook/actions/workflows/deploy-showcase.yml)

A personal lab for building modern AI software, writing down what works, and turning experiments into small demos.

This is not a course repo or a role-prep packet. It is a builder's notebook: concepts, prototypes, debugging notes, patterns, and project writeups that show practical fluency with LLMs, RAG, agents, APIs, SDKs, cloud workflows, and AI product design.

## Start Here

1. Open the deployed Support Triage Review Console: [https://ai-engineering-notebook.vercel.app/support-triage](https://ai-engineering-notebook.vercel.app/support-triage). Use recorded mode for the public, zero-cost walkthrough; the access-code path makes a real model call, and review actions capture human feedback without another call.
2. Inspect the Agentic Workflow trace viewer: [https://pablodcruz.github.io/ai-engineering-notebook/docs/agentic-workflow.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/agentic-workflow.html).
3. Use the [GitHub Pages Support Triage mirror](https://pablodcruz.github.io/ai-engineering-notebook/docs/support-triage.html) when you want the explicitly labeled recorded experience with no live backend.
4. Compare prompt candidates in the Prompt Regression report: [https://pablodcruz.github.io/ai-engineering-notebook/docs/prompt-regression-report.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/prompt-regression-report.html).
5. Try the Enablement Assistant demo: [https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-assistant.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-assistant.html).
6. Review the Enablement Assistant eval report: [https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-eval-report.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-eval-report.html).
7. Open the StreamFlow analytics dashboard: [https://pablodcruz.github.io/ai-engineering-notebook/docs/streamflow-dashboard.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/streamflow-dashboard.html).
8. Use [00-meta/roadmap.md](00-meta/roadmap.md) to pick the next experiment.
9. Capture technical understanding in [01-concepts](01-concepts).
10. Build small runnable exercises in [02-labs](02-labs).
11. Promote the best ideas into [03-projects](03-projects).
12. Turn useful explanations and diagrams into [04-explainers](04-explainers).
13. Collect polished demos and writeups in [06-showcase](06-showcase).

For a systematic architecture review, use the [AI System Review Checklist](05-reference/ai-system-review-checklist.md). For the distinction between tests, evals, traces, and monitoring, read [Evaluation And Observability](01-concepts/evaluation-observability.md).

## Fast Validation

Run the full local quality gate:

```bash
python scripts/validate_workspace.py
```

This checks documentation links, eval export freshness, runnable project tests, the Enablement Assistant evaluation set, and every lab's readiness contract.

## Showcase App

Open the canonical live application:

[https://ai-engineering-notebook.vercel.app/support-triage](https://ai-engineering-notebook.vercel.app/support-triage)

The live path is deliberately bounded: it accepts three synthetic cases, requires an access code, validates an exact response schema, uses a shared Redis daily ceiling, and exposes safe request telemetry. Recorded mode is always available without a provider call.

View the static portfolio and zero-cost mirrors:

[https://pablodcruz.github.io/ai-engineering-notebook/docs/](https://pablodcruz.github.io/ai-engineering-notebook/docs/)

View the StreamFlow analytics dashboard:

[https://pablodcruz.github.io/ai-engineering-notebook/docs/streamflow-dashboard.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/streamflow-dashboard.html)

Try the Enablement Assistant RAG demo:

[https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-assistant.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-assistant.html)

Review the Enablement Assistant eval report:

[https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-eval-report.html](https://pablodcruz.github.io/ai-engineering-notebook/docs/enablement-eval-report.html)

Source lives in [docs/index.html](docs/index.html).

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fpablodcruz%2Fai-engineering-notebook&project-name=ai-engineering-notebook-showcase)

Vercel is the canonical runtime for the Support Triage Review Console because it serves the Python API functions. GitHub Pages serves the static portfolio and explicitly recorded demos under `/docs/`. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Senior Engineer Review Path

If you are reviewing this workspace quickly, start with:

1. [Senior Review Guide](00-meta/senior-review-guide.md) for the review rubric and strongest evidence path.
2. [Agentic Workflow Demo](03-projects/agentic-workflow-demo.md) and [trace viewer](docs/agentic-workflow.html) for tool contracts, approval boundaries, refusal behavior, and observable execution.
3. [Prompt Regression Runner](03-projects/prompt-regression-runner.md), [comparison report](docs/prompt-regression-report.html), and [facilitator guide](04-explainers/prompt-evaluation-facilitator-guide.md) for prompt versioning, structured regression checks, and trainer delivery.
4. [Support Triage Review Console](03-projects/live-support-triage-studio.md), [self-deployment guide](docs/deploy-support-triage.html), and [operating-economics explainer](04-explainers/ai-app-operating-economics.md) for a customer-facing workflow that connects generation, validation, human correction, cost controls, operations, and prompt evaluation evidence.
4. [Enablement Assistant RAG](03-projects/enablement-assistant-rag.md), [deployed RAG demo](docs/enablement-assistant.html), and [eval report](docs/enablement-eval-report.html) for grounded-answer architecture, evaluation, and citations.
5. [Local AI Lab Runner](03-projects/local-ai-lab-runner.md) for developer experience, readiness checks, and CLI design.
6. [StreamFlow Phase 1](03-projects/streamflow-phase-1.md) for containerized stream processing, Spark, Airflow, and data quality.
7. [StreamFlow Phase 2](03-projects/streamflow-phase-2.md) for Snowflake medallion layers, analytics modeling, Power BI semantics, and reconciliation checks.
8. [Showcase Index](06-showcase/showcase-index.md) for the strongest demo-ready artifacts.
9. [Debugging Playbook](04-explainers/debugging-playbook.md) for operational thinking and troubleshooting judgment.

## Workspace Map

| Folder | Purpose |
| --- | --- |
| `00-meta` | Roadmap, build themes, and notebook conventions. |
| `01-concepts` | Notes on LLMs, prompting, RAG, agents, APIs, cloud workflows, evaluation, and observability. |
| `02-labs` | Small experiments with setup steps, expected output, and failure notes. |
| `03-projects` | Larger builds that combine concepts into useful AI tools. |
| `04-explainers` | Clear writeups, diagrams, and talk tracks for explaining what was built. |
| `05-reference` | Glossary, resource log, and a reusable AI-system review checklist. |
| `06-showcase` | Polished project summaries, demos, screenshots, and portfolio-style notes. |

## Build Loop

Each cycle should produce something concrete:

- Learn one concept deeply enough to explain it.
- Build one small thing that exercises the concept.
- Break it on purpose and document the failure mode.
- Improve the design, prompt, retrieval flow, tool boundary, or developer experience.
- Write down the practical takeaway.

## Current Themes

- Prompt design for reliable structured outputs.
- Retrieval-augmented generation over small trusted corpora.
- Tool-using agents with narrow permissions and observable steps.
- API and SDK integration patterns.
- Cloud-adjacent AI app architecture.
- Data engineering and streaming platform foundations.
- Analytics engineering with warehouse modeling and BI validation.
- Debuggable developer workflows for AI prototypes.
