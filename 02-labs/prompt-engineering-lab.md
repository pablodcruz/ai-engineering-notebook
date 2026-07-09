# Prompt Engineering Lab

## Skill Level

Beginner-friendly, with optional deeper implementation notes.

## Duration

30 to 45 minutes.

## Learning Objectives

- Improve vague prompts into task-specific prompts.
- Use context, constraints, and output formats.
- Compare model outputs and explain why one prompt performs better.

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

## Variations

- Add few-shot examples.
- Require JSON output.
- Add tone constraints for customer-facing communication.
- Add a hallucination trap with missing information.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Output is too generic | Prompt lacks task and audience | Add role, task, and success criteria. |
| Output invents details | Prompt does not constrain source use | Add "use only provided text" and missing-info handling. |
| Output is hard to parse | No format specified | Require bullets, table, or JSON schema. |

## Build Notes

Capture the difference between "better writing" and "better task design." The goal is not a prettier prompt; the goal is a more reliable workflow.
