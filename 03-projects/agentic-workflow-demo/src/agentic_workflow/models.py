from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BacklogTask:
    task_id: str
    title: str
    description: str
    status: str
    priority: str
    owner: str
    labels: tuple[str, ...] = ()
    blocked_by: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BacklogTask:
        return cls(
            task_id=str(payload["task_id"]),
            title=str(payload["title"]),
            description=str(payload["description"]),
            status=str(payload["status"]),
            priority=str(payload["priority"]),
            owner=str(payload["owner"]),
            labels=tuple(str(value) for value in payload.get("labels", [])),
            blocked_by=tuple(str(value) for value in payload.get("blocked_by", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["labels"] = list(self.labels)
        payload["blocked_by"] = list(self.blocked_by)
        return payload


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, str]
    read_only: bool
    requires_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PendingAction:
    tool: str
    arguments: dict[str, Any]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceStep:
    step: int
    event: str
    name: str
    input: dict[str, Any]
    output: dict[str, Any]
    status: str
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    request: str
    status: str
    answer: str
    sources: list[str] = field(default_factory=list)
    trace: list[TraceStep] = field(default_factory=list)
    pending_action: PendingAction | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "status": self.status,
            "answer": self.answer,
            "sources": self.sources,
            "pending_action": self.pending_action.to_dict() if self.pending_action else None,
            "trace": [step.to_dict() for step in self.trace],
        }
