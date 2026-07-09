# Prompt Engineering

## Why This Matters

Show learners how to design prompts that produce reliable, useful outputs for a specific task.

## Practical Pattern

Use this structure when teaching:

1. Task: what should the model do?
2. Context: what information should it use?
3. Constraints: what rules must it follow?
4. Output format: what should the answer look like?
5. Examples: what good output looks like.
6. Checks: how the output should be evaluated.

## Techniques

- Role and task framing.
- Clear success criteria.
- Few-shot examples.
- Structured output formats.
- Step decomposition.
- Grounding with supplied context.
- Refusal and uncertainty instructions.
- Iterative refinement based on observed failures.

## When Prompting Is Not Enough

Prompt engineering alone may not solve:

- Missing or private knowledge.
- Need for fresh data.
- Multi-step tool use.
- Strict compliance requirements.
- Deterministic business logic.
- High-volume evaluation and monitoring.

## Engineering Lens

A prompt is part of the product contract. Treat it like code that needs versioning, tests, and rollback discipline.

Design decisions to make explicit:

- Which input fields are allowed into the prompt?
- Which instructions are stable system behavior versus task-specific context?
- Which output fields are required?
- What validation happens after the model responds?
- What user-facing fallback appears when validation fails?

## What To Evaluate

- Output completeness against a rubric.
- Format validity for structured outputs.
- Hallucination behavior when source information is missing.
- Sensitivity to prompt wording changes.
- Regression behavior across a fixed test set.

## Lab Idea

Create a messy support ticket and ask learners to:

- Summarize it.
- Extract structured fields.
- Classify urgency.
- Draft a customer response.
- Improve the prompt after seeing a bad output.

## Explain It Back

Describe how a prompt becomes part of an application workflow rather than just a clever chat message.
