from __future__ import annotations

from typing import Any

from .backlog import BacklogRepository
from .models import ToolSpec


class ApprovalRequired(PermissionError):
    """Raised when a mutating tool is called without explicit approval."""


TOOL_SPECS = (
    ToolSpec(
        name="search_backlog",
        description="Find backlog tasks by text and optional status.",
        input_schema={"query": "string", "status": "optional string"},
        read_only=True,
    ),
    ToolSpec(
        name="get_task",
        description="Return the complete record for one task id.",
        input_schema={"task_id": "string"},
        read_only=True,
    ),
    ToolSpec(
        name="draft_summary",
        description="Draft a cited summary for an explicit list of task ids.",
        input_schema={"task_ids": "list[string]"},
        read_only=True,
    ),
    ToolSpec(
        name="update_priority",
        description="Simulate changing one task priority in the in-memory backlog.",
        input_schema={"task_id": "string", "priority": "low|medium|high|critical"},
        read_only=False,
        requires_approval=True,
    ),
)


class BacklogTools:
    def __init__(self, repository: BacklogRepository) -> None:
        self.repository = repository
        self.specs = {spec.name: spec for spec in TOOL_SPECS}

    def call(self, name: str, arguments: dict[str, Any], *, approved: bool = False) -> dict[str, Any]:
        spec = self.specs.get(name)
        if spec is None:
            raise ValueError(f"Tool is not allowed: {name}")
        if spec.requires_approval and not approved:
            raise ApprovalRequired(f"{name} requires explicit approval")

        if name == "search_backlog":
            tasks = self.repository.search(
                query=str(arguments.get("query", "")),
                status=str(arguments["status"]) if arguments.get("status") else None,
            )
            return {
                "count": len(tasks),
                "tasks": [self._summary(task) for task in tasks],
                "sources": [self.repository.source_for(task.task_id) for task in tasks],
            }
        if name == "get_task":
            task_id = str(arguments["task_id"]).upper()
            task = self.repository.get(task_id)
            if task is None:
                return {"found": False, "task_id": task_id, "sources": []}
            return {"found": True, "task": task.to_dict(), "sources": [self.repository.source_for(task_id)]}
        if name == "draft_summary":
            task_ids = [str(value).upper() for value in arguments.get("task_ids", [])]
            tasks = [task for task_id in task_ids if (task := self.repository.get(task_id)) is not None]
            lines = [
                f"{task.task_id}: {task.title} ({task.status}, {task.priority}, owner {task.owner})"
                for task in tasks
            ]
            summary = f"Backlog summary for {len(tasks)} task(s): " + "; ".join(lines)
            return {
                "summary": summary,
                "task_ids": [task.task_id for task in tasks],
                "sources": [self.repository.source_for(task.task_id) for task in tasks],
            }
        if name == "update_priority":
            task_id = str(arguments["task_id"]).upper()
            priority = str(arguments["priority"]).lower()
            if priority not in {"low", "medium", "high", "critical"}:
                raise ValueError(f"Unsupported priority: {priority}")
            before = self.repository.get(task_id)
            if before is None:
                raise KeyError(f"Unknown task: {task_id}")
            after = self.repository.update_priority(task_id, priority)
            return {
                "simulated": True,
                "task_id": task_id,
                "before": before.priority,
                "after": after.priority,
                "sources": [self.repository.source_for(task_id)],
            }
        raise AssertionError(f"Unhandled tool: {name}")

    @staticmethod
    def _summary(task) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "owner": task.owner,
        }
