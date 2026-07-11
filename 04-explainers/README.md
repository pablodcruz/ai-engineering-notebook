# Explainers

This folder turns implementation lessons into material that can be used with engineers, product teams, operators, and learners. The goal is not to repeat project documentation; it is to make the reasoning teachable.

## Guide

| Explainer | Use it for |
| --- | --- |
| [Layered explanations](layered-explanations.md) | Translating the same AI concept for technical, product, and general audiences. |
| [Debugging playbook](debugging-playbook.md) | Diagnosing environment, integration, model, retrieval, and agent failures systematically. |
| [Production-readiness checklist](production-readiness-checklist.md) | Reviewing what must change before a prototype handles real users or data. |
| [AI application operating economics](ai-app-operating-economics.md) | Explaining inference cost, quotas, access patterns, and bounded public demos. |
| [Prompt evaluation facilitator guide](prompt-evaluation-facilitator-guide.md) | Running a customer-facing session around prompt comparison and evaluation evidence. |
| [Demo script template](demo-script-template.md) | Preparing a short demonstration with a happy path, failure path, and practical takeaway. |

## A Strong Explanation Should

- Begin with the user or business decision, not model terminology.
- Separate deterministic software behavior from probabilistic model behavior.
- Name one failure mode and how the system detects it.
- Make limitations and production boundaries explicit.
- End with a decision, question, or action for the audience.

## Reusable Delivery Pattern

1. State the workflow problem in one sentence.
2. Show the smallest successful path.
3. Expose the application controls around the model.
4. Demonstrate a failure or refusal honestly.
5. Connect the run to tests, evals, or human review.
6. Ask what must change for the audience’s environment.

The strongest live example is the [Support Triage Review Console](../docs/support-triage.html), which connects model generation, validation, cost controls, human correction, and evaluation evidence in one walkthrough.
