# Prompt Engineering Lab

## Skill Level

Beginner-friendly, with optional deeper implementation notes.

## Duration

30 to 45 minutes.

## Learning Objectives

- Improve vague prompts into task-specific prompts.
- Use context, constraints, and output formats.
- Compare model outputs and explain why one prompt performs better.
- Identify when prompt changes are not enough and validation is needed.

## Prerequisites

- Access to a chat model or a saved set of model outputs.
- A short sample input, such as a customer support ticket.
- Basic understanding of task, context, constraints, and output format.

## Setup

1. Choose one messy input example.
2. Save the original vague prompt.
3. Decide what a useful answer must include.
4. Prepare a simple comparison table for prompt version, output, strengths, and gaps.

## Exercise

Start with a vague prompt:

```text
Summarize this customer issue and tell me what to do.
```

Improve it into a structured prompt:

```text
You are assisting a support operations team.
Summarize the customer issue using only the provided ticket text.
Return:
- customer problem
- likely product area
- urgency: low, medium, or high
- missing information
- recommended next response
If the ticket does not contain enough information, say what is missing.
```

Then run this sequence:

1. Capture the vague prompt output.
2. Capture the structured prompt output.
3. Add one format constraint, such as JSON or a table.
4. Add a missing-information constraint.
5. Compare which output is easier to trust and why.

## Expected Output

The lab should produce:

- At least two prompt versions.
- A side-by-side comparison of outputs.
- A short explanation of why the stronger prompt is more reliable.
- One remaining risk that prompt wording alone does not solve.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Output is too generic | Prompt lacks task and audience | Add role, task, and success criteria. |
| Output invents details | Prompt does not constrain source use | Add "use only provided text" and missing-info handling. |
| Output is hard to parse | No format specified | Require bullets, table, or JSON schema. |
| Output follows format but is wrong | No validation or source checks | Add review criteria or automated checks. |

## Build Notes

Capture the difference between "better writing" and "better task design." The goal is not a prettier prompt; the goal is a more reliable workflow.

Useful variations:

- Add few-shot examples.
- Require JSON output.
- Add tone constraints for customer-facing communication.
- Add a hallucination trap with missing information.

## Debrief

- Which prompt change improved reliability the most?
- Which output looked polished but still had a correctness risk?
- What would you validate in code if this became part of an application?
- Where would you draw the line between prompt engineering and product logic?
