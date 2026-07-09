# Agents Tool-Use Lab

## Skill Level

Intermediate.

## Duration

45 to 60 minutes.

## Learning Objectives

- Explain what makes a workflow agentic.
- Define a small set of safe tools.
- Observe tool calls and model decisions.
- Discuss guardrails and stopping conditions.
- Separate model choice from application permissions.

## Prerequisites

- Basic understanding of tool calling or function calling.
- A tiny structured data source, such as a project backlog in JSON or markdown.
- A place to log tool calls, observations, and final output.
- Optional: model API credentials if using a live model.

## Setup

1. Create a tiny backlog with three to five tasks.
2. Define the allowed tool list before writing prompts.
3. Decide which actions are read-only and which require confirmation.
4. Prepare a trace table with columns for step, tool, input, observation, and decision.

## Exercise

Build an assistant that can answer questions about a small project backlog and create a draft task summary. The only allowed tools are:

- Search backlog.
- Get task details.
- Draft summary.

Run this sequence:

1. Define tool schemas.
2. Give the model a goal and constraints.
3. Let the model choose tools.
4. Log each tool call and observation.
5. Stop after the summary is drafted.
6. Review whether the result followed constraints.

## Expected Output

The lab should produce:

- A tool list with clear names, inputs, and outputs.
- A trace of at least two tool calls.
- A draft task summary.
- A note explaining whether the workflow respected permissions and stopping conditions.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Agent calls tools repeatedly | No loop limit or unclear stop condition | Add a maximum step count and explicit completion criteria. |
| Agent uses the wrong tool | Tool names or descriptions overlap | Make tool responsibilities narrow and distinct. |
| Agent invents backlog details | Tool output is not treated as source of truth | Require summaries to cite tool observations. |
| Irreversible action happens too early | Missing approval boundary | Require user confirmation before writes or external actions. |
| Trace is hard to debug | Tool inputs and outputs are not logged | Log every tool call, observation, and final decision. |

## Build Notes

Emphasize that agent design is software design. The model chooses actions, but the application owns permissions, controls, and accountability.

Safety notes:

- Keep tools narrow.
- Require user confirmation before irreversible actions.
- Log intermediate steps.
- Set loop limits.
- Treat tool output as data that still needs validation.

## Debrief

- Which tool boundary was easiest to explain?
- Which step created the most risk?
- Did the model stop at the right time?
- What would you add before using this pattern with real business data?
