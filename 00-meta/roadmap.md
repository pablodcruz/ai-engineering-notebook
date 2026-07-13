# Roadmap

This roadmap tracks portfolio outcomes, not just ideas. Keep one milestone active, finish it to the workspace quality gate, and move it to Shipped before starting another flagship project.

## Shipped

| Artifact | Evidence |
| --- | --- |
| Enablement Assistant RAG | Runnable lexical retrieval, grounded answers, citations, refusal behavior, tests, evals, a static demo, and an exported eval report. |
| Local AI Lab Runner | Runnable readiness CLI, structured findings, failure simulation, tests, and lab contract validation. |
| StreamFlow Phase 1 | Synthetic event producer, data quality logic, Redpanda/Spark/Airflow architecture, local tests, and documented smoke tests. |
| StreamFlow Phase 2 | Snowflake Bronze/Silver/Gold SQL, reconciliation checks, Airflow orchestration, Power BI contracts, and a static dashboard. |
| Agentic Workflow Demo | Typed tools, approval-gated simulated mutation, structured traces, behavioral evals, and a static trace viewer. |
| RAG Evaluation Hardening | Balanced 18-case suite with citation-line checks, answer traits, partial-coverage refusal, adversarial cases, and CI-portable corpus exclusions. |
| Prompt Regression Runner | Fifteen fixed support cases, two prompt candidates, eight deterministic checks, optional live recording, a comparison report, and a facilitator guide. |
| Support Triage Review Console | Deployed synthetic live/recorded workflow, schema validation, layered cost controls, human accept/correct decisions, browser-local metrics, sanitized feedback export, and safe self-deployment. |
| Portfolio showcase | GitHub Pages deployment, project review path, documentation link checks, and one-command workspace validation. |
| Repository documentation roundup | Folder guides, concept-to-evidence navigation, evaluation and observability guidance, expanded debugging workflow, shared terminology, and a reusable AI-system review checklist. |
| Engineering quality automation | Pinned Ruff, mypy, and coverage tooling; shared root configuration; an 80% branch-aware floor; CI artifacts; and one optional local quality mode. |
| Support Triage browser automation | Six isolated Chromium tests covering recorded recommendations, human accept/correct decisions, metrics, sanitized export, reset, access-request links, and the feedback candidate report without secrets or model calls. |
| Review Feedback To Evaluation Pipeline | Strict synthetic export validation, accept/override summaries, correction deduplication, candidate regression cases, explicit approval artifacts, tests, and a deployed recorded report without automatic golden-set promotion. |

## Active: Bounded StreamFlow Integration Smoke Test

Prove that the Phase 1 components can exchange a small synthetic event through their real integration boundaries without requiring a long-running local stack for every validation run.

### Minimum Scope

- Start only the minimum required containerized services.
- Publish a bounded synthetic event batch.
- Verify accepted and rejected records at the processing boundary.
- Tear down cleanly and preserve actionable failure output.

### Definition Of Done

- The smoke test has a deterministic timeout and bounded resource usage.
- It proves a real cross-component path rather than only unit behavior.
- CI remains reliable, with the integration test isolated from the fast default gate if needed.
- Setup, expected output, and common Docker failures are documented.

## Next

1. Add a mocked Zendesk-style support adapter.
2. Add an operational evidence dashboard for support-triage cost, latency, failures, and reviewer agreement.

## Later

### Prompted Workflows

- Structured support-ticket summarizer.
- JSON extractor with schema validation.
- Prompt comparison notebook.

### Retrieval And Knowledge Systems

- Chunking comparison experiment.
- Retrieval failure gallery.
- Hybrid retrieval and reranking experiment.
- Corpus freshness and permissions design.

### Cloud-Aware AI Apps

- Backend model gateway.
- Secret management implementation notes.
- Storage and retrieval-index lifecycle prototype.
- Observability, latency, and cost logging.

### Data Engineering For AI

- Spark data quality report over event data.
- Batch dataset profiling for AI readiness.
- dbt-based warehouse transformations and tests.
- Incremental ingestion with Snowpipe, Streams, or Tasks.

## Working Rhythm

Each milestone should follow the same loop:

1. Write the question or hypothesis.
2. Build the minimum working version.
3. Record setup steps and expected output.
4. Break it deliberately and document the failure modes.
5. Add tests or evals that preserve the lesson.
6. Publish a short explainer and demo path.
7. Link it from the showcase if it is worth sharing.

## Quality Gate

Before moving an artifact to Shipped, run:

```bash
python scripts/validate_workspace.py
```

Use [senior-review-guide.md](senior-review-guide.md) to judge whether the work demonstrates engineering judgment, not just implementation effort.
