# Production Readiness Checklist

Use this checklist when promoting a lab or prototype into a production-shaped AI application.

## Product Boundary

- The user problem is specific.
- The target user and workflow are named.
- The success criteria are observable.
- The system has a clear fallback when AI output is not good enough.

## Data And Grounding

- Source data is trusted, scoped, and versioned.
- Retrieval results are inspectable before generation.
- Answers cite source material when grounding matters.
- The system refuses unsupported questions instead of filling gaps.
- Stale or missing data has a visible failure mode.

## Model And Prompting

- Prompts separate task, context, constraints, and output format.
- Model-dependent behavior is covered by evals or review.
- Structured outputs are parsed and validated.
- Prompt changes can be compared against a fixed test set.

## Tools And Actions

- Tool permissions are narrow.
- Tool input and output schemas are explicit.
- Irreversible actions require human confirmation.
- Loops have step limits and stopping conditions.
- Tool observations are logged for debugging.

## Security And Privacy

- Secrets are loaded from environment or a secret manager.
- Logs avoid secret values and sensitive user data.
- Access control is designed before shared deployment.
- Source documents respect permission boundaries.
- External service calls have timeout and retry rules.

## Reliability And Operations

- A known-good smoke test exists.
- Environment readiness is checked before experiments.
- Tests and evals run from one command.
- CI runs the same quality gate used locally.
- Failures include suggested fixes.
- Cost, latency, and rate-limit behavior are observable before production.

## Demo Readiness

- The happy path is quick to run.
- One failure mode can be triggered or explained.
- The demo shows evidence, not only final output.
- The limitations are named plainly.
- The next production step is obvious.

