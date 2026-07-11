# Prompt Evaluation Facilitator Guide

## One-Sentence Point

Prompt evaluation means running candidate instructions against the same examples and checking whether the outputs satisfy an explicit product contract.

## Explain It At Three Levels

### Plain Language

Think of it as a driving test for a changed prompt. Every candidate gets the same route, and the evaluator checks important behaviors instead of deciding from one impressive answer.

### Product Language

The team defines what a useful support-triage result must contain, tests prompt candidates against representative tickets, and reviews both summary metrics and individual failures before promotion.

### Engineering Language

Versioned prompt candidates and fixed inputs produce recorded outputs. Deterministic schema and task checks generate case-level results, aggregate comparisons, and a regression gate. Optional live adapters generate new recordings without coupling CI to a model provider.

## 45-Minute Session Plan

| Time | Activity | Learning Goal |
| --- | --- | --- |
| 0–5 min | Ask what "better prompt" means | Surface hidden success criteria. |
| 5–12 min | Show one ticket and the vague prompt | Establish the baseline and likely failure modes. |
| 12–20 min | Introduce the eight checks | Separate syntax, task quality, grounding, and actionability. |
| 20–28 min | Run the candidate comparison | Show repeatability across a fixed dataset. |
| 28–35 min | Inspect T001 and T015 | Connect aggregate scores to concrete failures. |
| 35–40 min | Explain recorded versus live outputs | Clarify reproducibility, variability, credentials, and cost. |
| 40–45 min | Design one customer-specific case | Transfer the method into the audience's workflow. |

## Suggested Demonstration

```powershell
cd 03-projects\prompt-regression-runner
$env:PYTHONPATH='src'
python -m prompt_regression.cli compare recorded\baseline-v1.json recorded\structured-v2.json
python -m prompt_regression.cli case T001 recorded\baseline-v1.json recorded\structured-v2.json
python -m prompt_regression.cli case T015 recorded\baseline-v1.json recorded\structured-v2.json
```

Then open the [Live Support Triage Studio](../docs/support-triage.html). Run T001 live when the Vercel service is configured, inspect its contract and telemetry, and compare that single request with the 15-case regression evidence. If the service is unavailable, use **Load recorded example** and call out the mode change explicitly.

## Questions To Ask The Audience

- Which failures can software determine exactly?
- Which labels could reasonable reviewers disagree about?
- What customer data must never enter a committed recording?
- Which edge case would be most expensive to miss?
- Should a prompt be promoted if its average improves but one critical case regresses?
- Who owns the rubric after the initial deployment?

## Common Misconceptions

| Misconception | Reframe |
| --- | --- |
| "The harness gives the model tools." | This runner evaluates outputs; it does not execute model-selected actions. |
| "Valid JSON means the prompt works." | JSON proves parseability, not classification, completeness, or grounding. |
| "The highest score automatically wins." | Scores focus review; critical case failures can override the average. |
| "Recorded outputs are fake tests." | Reviewed recordings make scoring reproducible; live runs test model behavior separately. |
| "An LLM judge solves subjective evaluation." | Judges also need calibration, versioning, and human validation. |

## Failure Demo

Copy `structured-v2.json` to an ignored local file, change T001 urgency from `high` to `low`, and evaluate the copy. The runner should preserve every other passing check while identifying the exact regression.

Do not modify the committed recording during a live class unless you intend to regenerate the public comparison evidence afterward.

## Forward Deployed Follow-Through

After the session, facilitate a short customer working meeting:

1. Identify the real workflow decision the model supports.
2. Collect representative and high-cost failure examples.
3. Define deterministic checks before subjective rubrics.
4. Assign dataset and rubric ownership.
5. Agree on promotion thresholds and critical-case vetoes.
6. Decide when live evaluation, shadow traffic, and human review are required.
