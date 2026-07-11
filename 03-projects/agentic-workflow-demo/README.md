# Agentic Workflow Demo

A dependency-light backlog agent that demonstrates constrained tool use, explicit approval boundaries, observable traces, and behavioral evaluation without requiring a model API or external service.

## Quick Start

PowerShell:

```powershell
cd 03-projects\agentic-workflow-demo
$env:PYTHONPATH='src'
python -m agentic_workflow.cli tools
python -m agentic_workflow.cli run "Summarize blocked work"
python -m agentic_workflow.cli run "Change TASK-103 priority to high"
python -m agentic_workflow.cli run "Change TASK-103 priority to high" --approve
```

Bash or Git Bash:

```bash
cd 03-projects/agentic-workflow-demo
PYTHONPATH=src python -m agentic_workflow.cli run "Summarize blocked work"
```

Optional install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
backlog-agent run "Give me a backlog summary"
```

## Allowed Tools

| Tool | Permission | Purpose |
| --- | --- | --- |
| `search_backlog` | Read-only | Find tasks by text and status. |
| `get_task` | Read-only | Inspect one complete task record. |
| `draft_summary` | Read-only | Summarize an explicit set of retrieved task ids. |
| `update_priority` | Approval required | Simulate an in-memory priority change. |

Requests to delete, close, assign, deploy, or send messages are refused because no corresponding tool is allowed.

## Commands

```powershell
backlog-agent tools --json
backlog-agent run "What is happening with TASK-103?" --json
backlog-agent run "Change TASK-103 priority to critical"
backlog-agent run "Change TASK-103 priority to critical" --approve
backlog-agent eval
```

## Tests And Evals

```powershell
python -m unittest discover -s tests
$env:PYTHONPATH='src'; python -m agentic_workflow.cli eval
```

Unit tests cover repository behavior, tool permissions, approval enforcement, refusal, loop limits, simulated mutation, citations, and trace structure. Behavioral evals cover successful reads, required approval, approved execution, and prohibited actions.

## Prototype Boundary

The planner is deterministic so the safety and observability contracts remain inspectable without a live model. A production version could place a model-backed planner in front of the same tool registry, while the application continues to own tool validation, approval enforcement, step limits, and audit logging.
