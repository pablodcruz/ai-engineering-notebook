from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "03-projects" / "enablement-assistant"
DEFAULT_OUTPUT = ROOT / "docs" / "enablement-eval-data.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from enablement_assistant.answer import synthesize_answer  # noqa: E402
from enablement_assistant.cli import DEFAULT_QUESTIONS, _build_retriever, _load_questions  # noqa: E402


DEFAULT_EXCLUDES = [
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".cache",
    "tests",
    "fixtures",
    "enablement-assistant",
    "enablement-assistant-rag.md",
    "enablement-assistant.html",
    "enablement-eval-report.html",
    "enablement-eval-data.json",
    "lab-template.md",
    "project-template.md",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Enablement Assistant eval evidence for the static showcase.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the output file does not already match the current eval export.",
    )
    args = parser.parse_args()

    payload = build_payload(args.questions, args.top_k)
    rendered = json.dumps(payload, indent=2) + "\n"

    if args.check:
        if not args.output.exists():
            print(f"Missing eval export: {args.output}")
            return 1
        current = args.output.read_text(encoding="utf-8")
        if current != rendered:
            print(f"Eval export is stale: {args.output}")
            print("Run: python scripts/export_enablement_eval.py")
            return 1
        print(f"Eval export is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(payload['results'])} eval results to {args.output}")
    return 0


def build_payload(questions_path: Path, top_k: int) -> dict[str, object]:
    retriever = _build_retriever(ROOT, DEFAULT_EXCLUDES)
    questions = _load_questions(questions_path)
    results = []

    for item in questions:
        question = str(item["question"])
        expected_sources = list(item.get("expected_sources", []))
        should_answer = bool(item.get("should_answer", True))
        answer = synthesize_answer(question, retriever.search(question, top_k=top_k))
        retrieved_sources = [result.chunk.source_path for result in answer.retrieved]
        source_hit = not expected_sources or bool(set(expected_sources) & set(retrieved_sources))
        found_ok = answer.found is should_answer
        passed = source_hit and found_ok
        results.append(
            {
                "question": question,
                "expected_sources": expected_sources,
                "should_answer": should_answer,
                "found": answer.found,
                "source_hit": source_hit,
                "found_ok": found_ok,
                "passed": passed,
                "answer": answer.answer,
                "citations": [citation.__dict__ for citation in answer.citations],
                "retrieved": [
                    {
                        "rank": result.rank,
                        "score": round(result.score, 6),
                        "source_path": result.chunk.source_path,
                        "heading": result.chunk.heading,
                        "start_line": result.chunk.start_line,
                        "end_line": result.chunk.end_line,
                        "preview": result.chunk.preview,
                    }
                    for result in answer.retrieved
                ],
            }
        )

    passed_count = sum(1 for result in results if result["passed"])
    answered_count = sum(1 for result in results if result["found"])
    refusal_count = sum(1 for result in results if not result["found"])

    return {
        "metadata": {
            "project": "Enablement Assistant RAG",
            "questions_file": questions_path.relative_to(ROOT).as_posix(),
            "top_k": top_k,
            "corpus_root": ".",
            "retriever": "local lexical TF-IDF",
            "synthesizer": "extractive grounded answer",
        },
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "answered": answered_count,
            "refused": refusal_count,
            "source_hits": sum(1 for result in results if result["source_hit"]),
        },
        "results": results,
    }


if __name__ == "__main__":
    raise SystemExit(main())
