# Prompt Regression Runner

A trainer-friendly project for comparing prompt candidates against the same fixed support-ticket cases. It demonstrates how teams can treat prompts as versioned application components with repeatable regression evidence.

## Why "Runner" Instead Of "Harness"

In agent systems, a harness often means the runtime that gives a model access to tools or a computer. This project does something different: it runs prompt candidates against controlled cases and scores their outputs. The name makes that distinction explicit for learners who are new to AI engineering terminology.

## Quick Start

PowerShell:

```powershell
cd 03-projects\prompt-regression-runner
$env:PYTHONPATH='src'
python -m prompt_regression.cli compare recorded\baseline-v1.json recorded\structured-v2.json
python -m prompt_regression.cli case T001 recorded\baseline-v1.json recorded\structured-v2.json
```

Bash or Git Bash:

```bash
cd 03-projects/prompt-regression-runner
PYTHONPATH=src python -m prompt_regression.cli compare recorded/baseline-v1.json recorded/structured-v2.json
```

## What The Baseline Proves

The committed comparison uses 15 support tickets and two recorded candidates:

| Candidate | Intent | Current Result |
| --- | --- | --- |
| `baseline-v1` | Vague "summarize and tell me what to do" instruction | 55.0% of checks; 4/15 complete cases |
| `structured-v2` | Explicit task, allowed values, grounding rule, missing-information behavior, and JSON contract | 100% of checks; 15/15 complete cases |

Each case checks:

1. JSON validity.
2. Exact output schema.
3. Product-area classification.
4. Urgency classification.
5. Required problem details.
6. Missing-information coverage.
7. Absence of unsupported claims.
8. An actionable recommended response.

## Useful Commands

```powershell
python -m unittest discover -s tests
python -m prompt_regression.cli evaluate recorded\baseline-v1.json
python -m prompt_regression.cli evaluate recorded\structured-v2.json
python -m prompt_regression.cli case T015 recorded\baseline-v1.json recorded\structured-v2.json
```

## Optional Live Recording

CI never requires an API key. To create a new recording through the OpenAI Responses API:

```powershell
pip install -e ".[live]"
$env:OPENAI_API_KEY='your-local-key'
python -m prompt_regression.cli record-live `
  --candidate structured-live `
  --prompt prompts\structured-v2.md `
  --model YOUR_EXPLICIT_MODEL_ID `
  --output recorded\structured-live.local.json
```

The model id is required rather than silently defaulted so every recording identifies exactly what produced it. Keep experimental live recordings local until they have been reviewed for sensitive content and intentionally selected as evidence.

The adapter follows the official [Responses API](https://developers.openai.com/api/docs/guides/responses-vs-chat-completions) and [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) patterns. Prompt comparison remains model-agnostic because scoring consumes recorded JSON, not a provider-specific response object.

## Review Feedback Pipeline

The Support Triage Review Console exports sanitized, synthetic model-versus-human decisions.
The runner can validate that export and turn corrected decisions into candidate regression cases:

```powershell
python -m prompt_regression.cli prepare-feedback `
  feedback\recorded\support-triage-reviews.json `
  --output feedback\local\candidates.json `
  --report feedback\local\review-report.md
```

The pipeline fails on an unsupported schema, a false synthetic-data marker, unknown sample ids,
invalid decisions, contradictory outcomes, mismatched counts, and duplicate review ids. Accepted
decisions contribute to the summary but do not create new cases. Identical corrections are reduced
to one stable candidate so repeated browser reviews do not inflate the queue.

Each candidate preserves:

- The source case and review ids.
- The model suggestion and final human decision.
- The override reason and changed fields.
- A proposed regression case joined against the existing synthetic ticket.
- An `awaiting_human_review` promotion status.

After inspecting the candidates, record an explicit approval decision:

```powershell
python -m prompt_regression.cli approve-feedback `
  feedback\local\candidates.json `
  --reviewer "Reviewer name" `
  --approve F-T002-EXAMPLE `
  --output feedback\local\approval.json
```

An approval artifact does not modify `data/cases.jsonl`. The reviewer must still confirm the
policy decision, complete the deterministic expectations, and promote the case through a separate
reviewed code change. This prevents one correction from silently becoming permanent evaluation
truth.

Open the [deployed candidate report](../../docs/feedback-candidate-report.html) for recorded evidence
or run `python ../../scripts/export_feedback_candidates.py --check` to verify that its data is current.

## Trainer Demo Path

1. Explain that the same 15 tickets go to both candidates.
2. Run `compare` and show the aggregate gap.
3. Run `case T001` to expose invalid JSON and missing fields in the vague candidate.
4. Run `case T015` to show why ambiguity handling belongs in the product contract.
5. Open the static comparison report and inspect failures by check.
6. Change one recorded field in a copy and rerun the evaluator to demonstrate regression detection.
7. Close by asking which checks should remain deterministic and which require human judgment.

## Prototype Boundary

- Recorded outputs are teaching fixtures, not claims about a specific model.
- Keyword expectations make the baseline easy to inspect but do not capture semantic equivalence.
- The runner does not use an LLM-as-judge.
- Latency and token usage are preserved by live recordings but are not scored in the deterministic baseline.
- Production use needs dataset ownership, review policy, privacy controls, and calibrated human rubrics.
- The feedback workflow accepts only the three published synthetic demo cases; arbitrary customer
  exports and ticket text are intentionally unsupported.
