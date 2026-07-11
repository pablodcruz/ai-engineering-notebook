from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

from .models import BacklogTask


class BacklogRepository:
    def __init__(self, tasks: list[BacklogTask], source_name: str = "data/backlog.json") -> None:
        self._tasks = {task.task_id: task for task in tasks}
        self.source_name = source_name

    @classmethod
    def from_json(cls, path: Path) -> "BacklogRepository":
        payload = json.loads(path.read_text(encoding="utf-8"))
        tasks = [BacklogTask.from_dict(item) for item in payload["tasks"]]
        source_name = f"data/{path.name}" if path.parent.name == "data" else path.name
        return cls(tasks, source_name=source_name)

    def search(self, query: str = "", status: str | None = None) -> list[BacklogTask]:
        terms = [term for term in query.lower().split() if term not in {"*", "all", "backlog", "work"}]
        matches = []
        for task in self._tasks.values():
            if status and task.status != status:
                continue
            haystack = " ".join(
                [task.task_id, task.title, task.description, task.status, task.priority, task.owner, *task.labels]
            ).lower()
            if terms and not all(term in haystack for term in terms):
                continue
            matches.append(task)
        return sorted(matches, key=lambda task: task.task_id)

    def get(self, task_id: str) -> BacklogTask | None:
        return self._tasks.get(task_id.upper())

    def update_priority(self, task_id: str, priority: str) -> BacklogTask:
        task = self.get(task_id)
        if task is None:
            raise KeyError(f"Unknown task: {task_id}")
        updated = replace(task, priority=priority)
        self._tasks[updated.task_id] = updated
        return updated

    def source_for(self, task_id: str) -> str:
        return f"{self.source_name}#{task_id.upper()}"
