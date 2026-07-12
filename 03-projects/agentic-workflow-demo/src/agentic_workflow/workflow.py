from __future__ import annotations

import re
from pathlib import Path
from time import perf_counter
from typing import Any

from .backlog import BacklogRepository
from .models import PendingAction, TraceStep, WorkflowResult
from .tools import BacklogTools

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BACKLOG = PROJECT_ROOT / "data" / "backlog.json"
TASK_PATTERN = re.compile(r"\bTASK-\d+\b", re.IGNORECASE)
PRIORITY_PATTERN = re.compile(r"\b(low|medium|high|critical)\b", re.IGNORECASE)


class StepLimitExceeded(RuntimeError):
    pass


class BacklogAgent:
    def __init__(self, tools: BacklogTools, *, max_tool_calls: int = 8) -> None:
        self.tools = tools
        self.max_tool_calls = max_tool_calls
        self._trace: list[TraceStep] = []
        self._tool_calls = 0
        self._sources: list[str] = []

    def run(self, request: str, *, approved: bool = False) -> WorkflowResult:
        self._trace = []
        self._tool_calls = 0
        self._sources = []
        normalized = request.strip()
        lowered = normalized.lower()

        try:
            if self._is_unsupported_mutation(lowered):
                return self._refuse(
                    normalized, "The requested mutation is outside the allowed tool set."
                )

            task_match = TASK_PATTERN.search(normalized)
            priority_match = PRIORITY_PATTERN.search(normalized)
            if self._is_priority_change(lowered) and task_match and priority_match:
                return self._change_priority(
                    normalized,
                    task_match.group(0).upper(),
                    priority_match.group(1).lower(),
                    approved=approved,
                )

            if "block" in lowered:
                self._decision("inspect_blockers", {"reason": "Request asks about blocked work."})
                found = self._call("search_backlog", {"query": "*", "status": "blocked"})
                task_ids = [task["task_id"] for task in found["tasks"]]
                for task_id in task_ids:
                    self._call("get_task", {"task_id": task_id})
                summary = self._call("draft_summary", {"task_ids": task_ids})
                return self._complete(normalized, summary["summary"])

            if task_match:
                task_id = task_match.group(0).upper()
                self._decision("inspect_task", {"task_id": task_id})
                result = self._call("get_task", {"task_id": task_id})
                if not result["found"]:
                    return self._complete(normalized, f"No backlog task named {task_id} was found.")
                task = result["task"]
                answer = (
                    f"{task_id}: {task['title']} is {task['status']} with {task['priority']} priority, "
                    f"owned by {task['owner']}. {task['description']}"
                )
                return self._complete(normalized, answer)

            if any(term in lowered for term in ("summary", "summarize", "overview", "active work")):
                self._decision(
                    "summarize_backlog", {"reason": "Request asks for a backlog overview."}
                )
                found = self._call("search_backlog", {"query": "*"})
                task_ids = [task["task_id"] for task in found["tasks"]]
                summary = self._call("draft_summary", {"task_ids": task_ids})
                return self._complete(normalized, summary["summary"])

            if lowered.startswith("find ") or lowered.startswith("search "):
                query = re.sub(r"^(find|search)( the)?( backlog)?( for)?\s+", "", lowered).strip()
                self._decision("search_backlog", {"query": query})
                found = self._call("search_backlog", {"query": query})
                task_ids = [task["task_id"] for task in found["tasks"]]
                if not task_ids:
                    return self._complete(normalized, "No matching backlog tasks were found.")
                summary = self._call("draft_summary", {"task_ids": task_ids})
                return self._complete(normalized, summary["summary"])

            return self._refuse(normalized, "The request is outside this agent's backlog scope.")
        except (KeyError, ValueError, StepLimitExceeded) as exc:
            self._add_trace("final", "workflow_error", {}, {"message": str(exc)}, "error", 0.0)
            return WorkflowResult(normalized, "error", str(exc), self._sources, list(self._trace))

    def _change_priority(
        self, request: str, task_id: str, priority: str, *, approved: bool
    ) -> WorkflowResult:
        arguments = {"task_id": task_id, "priority": priority}
        self._decision("propose_priority_change", arguments)
        current = self._call("get_task", {"task_id": task_id})
        if not current["found"]:
            return self._complete(request, f"No backlog task named {task_id} was found.")

        pending = PendingAction(
            tool="update_priority",
            arguments=arguments,
            reason="Changing task priority is a mutating action and requires explicit approval.",
        )
        if not approved:
            self._add_trace(
                "approval",
                "update_priority",
                arguments,
                {"reason": pending.reason},
                "pending",
                0.0,
            )
            answer = f"Approval required before changing {task_id} priority to {priority}."
            self._add_trace("final", "approval_required", {}, {"answer": answer}, "pending", 0.0)
            return WorkflowResult(
                request, "approval_required", answer, self._sources, list(self._trace), pending
            )

        self._add_trace(
            "approval", "update_priority", arguments, {"approved": True}, "approved", 0.0
        )
        changed = self._call("update_priority", arguments, approved=True)
        answer = (
            f"Simulated priority change for {task_id}: {changed['before']} -> {changed['after']}. "
            "The fixture file was not modified."
        )
        return self._complete(request, answer)

    def _call(
        self, name: str, arguments: dict[str, Any], *, approved: bool = False
    ) -> dict[str, Any]:
        if self._tool_calls >= self.max_tool_calls:
            raise StepLimitExceeded(f"Tool-call limit reached ({self.max_tool_calls})")
        self._tool_calls += 1
        started = perf_counter()
        try:
            output = self.tools.call(name, arguments, approved=approved)
        except Exception as exc:
            duration = (perf_counter() - started) * 1000
            self._add_trace("tool_result", name, arguments, {"error": str(exc)}, "error", duration)
            raise
        duration = (perf_counter() - started) * 1000
        self._sources.extend(
            source for source in output.get("sources", []) if source not in self._sources
        )
        self._add_trace("tool_call", name, arguments, output, "ok", duration)
        return output

    def _decision(self, name: str, output: dict[str, Any]) -> None:
        self._add_trace("decision", name, {}, output, "ok", 0.0)

    def _complete(self, request: str, answer: str) -> WorkflowResult:
        self._add_trace(
            "final", "complete", {}, {"answer": answer, "sources": self._sources}, "ok", 0.0
        )
        return WorkflowResult(request, "completed", answer, self._sources, list(self._trace))

    def _refuse(self, request: str, reason: str) -> WorkflowResult:
        self._decision("refuse", {"reason": reason})
        self._add_trace("final", "refused", {}, {"answer": reason}, "refused", 0.0)
        return WorkflowResult(request, "refused", reason, [], list(self._trace))

    def _add_trace(
        self,
        event: str,
        name: str,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any],
        status: str,
        duration_ms: float,
    ) -> None:
        self._trace.append(
            TraceStep(
                step=len(self._trace) + 1,
                event=event,
                name=name,
                input=input_payload,
                output=output_payload,
                status=status,
                duration_ms=round(duration_ms, 3),
            )
        )

    @staticmethod
    def _is_priority_change(request: str) -> bool:
        return "priority" in request and any(
            term in request for term in ("change", "set", "update", "raise", "make")
        )

    @staticmethod
    def _is_unsupported_mutation(request: str) -> bool:
        return any(
            term in request
            for term in ("delete", "close task", "send email", "deploy", "assign task")
        )


def run_workflow(
    request: str,
    *,
    approved: bool = False,
    backlog_path: Path = DEFAULT_BACKLOG,
    max_tool_calls: int = 8,
) -> WorkflowResult:
    repository = BacklogRepository.from_json(backlog_path)
    tools = BacklogTools(repository)
    return BacklogAgent(tools, max_tool_calls=max_tool_calls).run(request, approved=approved)
