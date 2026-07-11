# Evaluation And Observability

## Why This Matters

AI systems can return valid HTTP responses and still fail the user. Evaluation measures whether the behavior is useful; observability supplies the evidence needed to explain what happened in a particular run. A reliable product needs both.

## Evaluation Versus Observability

| Discipline | Primary question | Typical evidence |
| --- | --- | --- |
| Tests | Did deterministic code satisfy its contract? | Assertions, exit codes, coverage. |
| Evals | Did model-dependent behavior meet task-specific expectations? | Fixed cases, rubrics, graders, human labels. |
| Observability | What happened during this request? | Request ids, latency, token usage, retrieval results, tool traces, error codes. |
| Monitoring | Is behavior changing across requests or time? | Rates, percentiles, alerts, drift and cost trends. |

These layers overlap, but they are not interchangeable. A schema test cannot judge whether a response is helpful. A human quality score cannot prove that an authorization check ran.

## Start With The Decision

Before choosing metrics, identify the decision the system supports:

1. What user outcome should improve?
2. What model behavior contributes to that outcome?
3. What deterministic application rules must always hold?
4. What failure is costly enough to require human review?
5. What evidence would let a reviewer reproduce or explain the result?

For support triage, the business decision is not “produce JSON.” It is “route and respond to a ticket appropriately.” JSON validity is necessary, while taxonomy accuracy, urgency, groundedness, and actionability determine usefulness.

## Building An Evaluation Set

A useful first evaluation set should contain:

- Normal cases that represent the common workflow.
- Boundary cases where labels are easily confused.
- Missing-information cases that should trigger uncertainty.
- Adversarial inputs that challenge instructions or data boundaries.
- Refusal cases that are outside the system’s supported scope.
- Previously observed failures promoted into regression cases.

Every case needs a reason for existing. Prefer a small reviewed set with clear failure meaning over a large pile of synthetic prompts with ambiguous labels.

## Choosing Checks

Use deterministic checks when the requirement is deterministic:

- Required keys and exact schema.
- Controlled category membership.
- Citation paths and source identifiers.
- Tool permissions and approval checkpoints.
- Maximum length and forbidden fields.

Use human or model-assisted grading when quality is subjective:

- Whether a summary preserves the customer’s actual problem.
- Whether a response is actionable and appropriately cautious.
- Whether retrieved evidence fully supports the answer.
- Whether tone matches the audience and situation.

Model-assisted graders should themselves be calibrated against human judgments. Their score is evidence, not ground truth.

## Request-Level Evidence

A production-shaped trace should make it possible to answer:

- Which application and prompt version ran?
- Which model or provider configuration was used?
- What inputs or source identifiers were selected without logging sensitive content?
- Which tools, retrieval results, approvals, or validation steps occurred?
- How long did each stage take?
- How many tokens or provider units were consumed?
- Did the final contract pass?
- Which application and provider request ids correlate the failure?

Log metadata deliberately. Raw prompts, credentials, customer tickets, and provider exception messages may contain sensitive information and should not be logged merely because they are convenient during development.

## Release Workflow

Treat prompts, retrieval settings, schemas, and tool policies as versioned behavior:

1. Record the current candidate as a baseline.
2. Run both candidates over the same fixed cases.
3. Inspect case-level differences, not only aggregate scores.
4. Reject changes that violate deterministic contracts.
5. Review subjective wins and regressions with domain owners.
6. Promote gradually and keep a rollback path.
7. Monitor live outcomes and turn reviewed failures into new cases.

## Failure Patterns

| Symptom | Likely blind spot | Next investigation |
| --- | --- | --- |
| Aggregate score rises but users complain | Dataset does not represent real work | Sample reviewed user failures and rebalance cases. |
| Schema passes but decisions are wrong | Checks measure shape, not task correctness | Add label, grounding, and actionability criteria. |
| Offline eval passes but production degrades | Runtime context differs | Compare prompt version, retrieval, model, and input distribution. |
| Errors cannot be reproduced | Missing correlation and stage metadata | Add application request ids and structured stage events. |
| Human overrides are high | Taxonomy, prompt, or policy mismatch | Group override reasons and review the dominant category. |

## Repository Evidence

- [Prompt Regression Runner](../03-projects/prompt-regression-runner.md) compares two prompt candidates across fixed support cases.
- [Enablement Assistant evaluation](../docs/enablement-eval-report.html) checks retrieval, citations, refusals, partial coverage, and adversarial behavior.
- [Agentic Workflow traces](../docs/agentic-workflow.html) expose tool selection, approvals, refusals, and stopping states.
- [Support Triage Review Console](../docs/support-triage.html) captures model-versus-human decisions and override reasons.

## Explain It Back

Explain why “the API returned 200” is not an AI quality metric, and describe one test, one eval, and one observable event for a support-triage workflow.
