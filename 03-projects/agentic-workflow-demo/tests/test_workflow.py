from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agentic_workflow.backlog import BacklogRepository
from agentic_workflow.tools import ApprovalRequired, BacklogTools
from agentic_workflow.workflow import DEFAULT_BACKLOG, BacklogAgent, run_workflow


class AgenticWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = BacklogRepository.from_json(DEFAULT_BACKLOG)
        self.tools = BacklogTools(self.repository)

    def test_search_backlog_filters_blocked_tasks(self) -> None:
        result = self.tools.call("search_backlog", {"query": "*", "status": "blocked"})

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["tasks"][0]["task_id"], "TASK-102")
        self.assertEqual(result["sources"], ["data/backlog.json#TASK-102"])

    def test_get_task_returns_source_aware_record(self) -> None:
        result = self.tools.call("get_task", {"task_id": "TASK-103"})

        self.assertTrue(result["found"])
        self.assertEqual(result["task"]["owner"], "Iris")
        self.assertEqual(result["sources"], ["data/backlog.json#TASK-103"])

    def test_mutating_tool_rejects_direct_unapproved_call(self) -> None:
        with self.assertRaises(ApprovalRequired):
            self.tools.call("update_priority", {"task_id": "TASK-103", "priority": "high"})

        self.assertEqual(self.repository.get("TASK-103").priority, "medium")

    def test_priority_change_pauses_before_mutation(self) -> None:
        result = run_workflow("Change TASK-103 priority to high")
        tool_names = [step.name for step in result.trace if step.event == "tool_call"]

        self.assertEqual(result.status, "approval_required")
        self.assertIsNotNone(result.pending_action)
        self.assertNotIn("update_priority", tool_names)

    def test_approved_priority_change_is_simulated_and_traced(self) -> None:
        result = run_workflow("Change TASK-103 priority to high", approved=True)
        update = next(
            step
            for step in result.trace
            if step.event == "tool_call" and step.name == "update_priority"
        )

        self.assertEqual(result.status, "completed")
        self.assertTrue(update.output["simulated"])
        self.assertEqual(update.output["before"], "medium")
        self.assertEqual(update.output["after"], "high")
        self.assertIn("fixture file was not modified", result.answer)

    def test_prohibited_action_is_refused_without_tool_calls(self) -> None:
        result = run_workflow("Delete TASK-101")

        self.assertEqual(result.status, "refused")
        self.assertFalse(any(step.event == "tool_call" for step in result.trace))

    def test_step_limit_stops_multi_tool_workflow(self) -> None:
        agent = BacklogAgent(self.tools, max_tool_calls=1)
        result = agent.run("Summarize blocked work")

        self.assertEqual(result.status, "error")
        self.assertIn("Tool-call limit reached", result.answer)

    def test_trace_is_ordered_and_contains_timing(self) -> None:
        result = run_workflow("Give me a backlog summary")

        self.assertEqual(
            [step.step for step in result.trace], list(range(1, len(result.trace) + 1))
        )
        self.assertTrue(all(step.duration_ms >= 0 for step in result.trace))
        self.assertEqual(result.trace[0].event, "decision")
        self.assertEqual(result.trace[-1].event, "final")


if __name__ == "__main__":
    unittest.main()
