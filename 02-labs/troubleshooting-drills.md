# Troubleshooting Drills

## Skill Level

Beginner to intermediate.

## Duration

30 to 45 minutes.

## Learning Objectives

- Diagnose common AI application failures with a calm process.
- Separate environment, code, credential, network, service, and model-output issues.
- Practice explaining debugging steps out loud.
- Capture fixes so the next experiment starts from a better baseline.

## Prerequisites

- Access to the notebook's debugging playbook.
- A terminal where you can inspect runtime and environment state.
- Optional: the Local AI Lab Runner for readiness checks.
- A timer for short diagnosis rounds.

## Setup

1. Pick three scenarios from the drill table.
2. Set a five-minute timer for each scenario.
3. Prepare a note with columns for symptom, first check, finding, fix, and takeaway.
4. Keep the debugging playbook open for reference.

## Exercise

Use this drill format:

1. State the symptom.
2. Ask one clarifying question.
3. Check the fastest likely cause.
4. Explain what you are doing out loud.
5. Apply or propose the fix.
6. Summarize the takeaway.

Run at least three scenarios:

| Scenario | Practice Response |
| --- | --- |
| API key missing | Check environment variable, shell session, and credential name. |
| Wrong Python environment | Confirm interpreter, virtual environment, and installed packages. |
| Dependency install fails | Check package name, network, permissions, and version compatibility. |
| Model returns unsupported format | Inspect raw output, adjust prompt, add schema or parser guard. |
| RAG retrieves irrelevant chunks | Inspect query, chunk text, metadata, and similarity results. |
| Local app works, deployed app fails | Compare environment variables, runtime versions, network access, and logs. |
| Broad product question interrupts debugging | Record the question, finish the technical diagnosis, then return to product implications. |
| Tool-using agent loops | Stop execution, inspect state, add loop limit and clearer stopping condition. |

## Expected Output

The lab should produce:

- Three completed drill notes.
- One example of a fast check that avoided unnecessary debugging.
- One takeaway that can be added to a future lab or project troubleshooting section.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Diagnosis jumps around | No first hypothesis | State the likely category before checking details. |
| Secret value gets exposed | Credential check prints the full key | Check presence only; never print the secret. |
| Fix is not reusable | The exact command or setting was not captured | Record the command, shell, and environment. |
| Model behavior is blamed too early | Environment or request failed first | Confirm runtime, package, credential, endpoint, and raw response. |
| Drill becomes a lecture | Too many explanations before action | Use the timed format and narrate one check at a time. |

## Build Notes

When discussing troubleshooting, emphasize:

- Calm process.
- Visible reasoning.
- Fast isolation of variables.
- Knowing when to use a workaround to preserve the experiment.

The goal is not to memorize every error. The goal is to build a reliable first response when something breaks.

## Debrief

- Which scenario did you diagnose fastest?
- Which scenario needed a clearer first check?
- What would you add to the debugging playbook?
- How would you teach this failure mode to someone new to AI engineering?
