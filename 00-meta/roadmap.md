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
| Portfolio showcase | GitHub Pages deployment, project review path, documentation link checks, and one-command workspace validation. |

## Active: Prompt Evaluation Harness

Build a deterministic harness for comparing structured-output prompts and preserving quality regressions.

### Minimum Scope

- Version prompt candidates and structured test inputs.
- Validate output schema before scoring content quality.
- Compare candidates on correctness, completeness, and format validity.
- Export reviewable case-level evidence to the showcase.

### Definition Of Done

- The baseline runs locally without credentials or network access.
- At least two prompt candidates run against a fixed regression set.
- Schema and answer-trait failures include actionable diagnostics.
- The workspace validator gates the harness and exported evidence.
- The project includes a demo script, limitations, and showcase entry.

## Next

1. Add one bounded StreamFlow integration smoke test to CI.
2. Add lightweight linting, formatting, type checking, and coverage reporting.

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
