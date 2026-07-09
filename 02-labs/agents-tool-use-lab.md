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

## Scenario

Build an assistant that can answer questions about a small project backlog and create a draft task summary. The only allowed tools are:

- Search backlog.
- Get task details.
- Draft summary.

## Exercise Steps

1. Define tool schemas.
2. Give the model a goal and constraints.
3. Let the model choose tools.
4. Log each tool call and observation.
5. Stop after the summary is drafted.
6. Review whether the result followed constraints.

## Safety Notes

- Keep tools narrow.
- Require user confirmation before irreversible actions.
- Log intermediate steps.
- Set loop limits.
- Treat tool output as data that still needs validation.

## Build Notes

Emphasize that agent design is software design. The model chooses actions, but the application owns permissions, controls, and accountability.
