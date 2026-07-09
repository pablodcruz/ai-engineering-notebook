from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .answer import synthesize_answer
from .documents import build_chunks, load_markdown_documents
from .retrieval import TfIdfRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_ROOT = PROJECT_ROOT.parents[1]
DEFAULT_QUESTIONS = PROJECT_ROOT / "evals" / "questions.jsonl"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ask":
        return ask(args)
    if args.command == "retrieve":
        return retrieve(args)
    if args.command == "index":
        return index(args)
    if args.command == "eval":
        return evaluate(args)

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="enablement-assistant",
        description="Ask grounded questions over a markdown notebook.",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=NOTEBOOK_ROOT,
        help="Markdown corpus root. Defaults to the notebook root.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[
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
        ],
        help="Directory or file name to exclude. Can be repeated.",
    )

    subparsers = parser.add_subparsers(dest="command")

    ask_parser = subparsers.add_parser("ask", help="Answer a question with citations.")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--top-k", type=int, default=5)
    ask_parser.add_argument("--show-context", action="store_true")
    ask_parser.add_argument("--json", action="store_true", dest="as_json")

    retrieve_parser = subparsers.add_parser("retrieve", help="Show retrieved chunks only.")
    retrieve_parser.add_argument("query")
    retrieve_parser.add_argument("--top-k", type=int, default=5)
    retrieve_parser.add_argument("--json", action="store_true", dest="as_json")

    index_parser = subparsers.add_parser("index", help="Build and save a portable chunk index.")
    index_parser.add_argument("--out", type=Path, default=PROJECT_ROOT / ".cache" / "notebook-index.json")

    eval_parser = subparsers.add_parser("eval", help="Run grounded-answer evaluation questions.")
    eval_parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    eval_parser.add_argument("--top-k", type=int, default=5)

    return parser


def ask(args: argparse.Namespace) -> int:
    retriever = _build_retriever(args.corpus, args.exclude)
    retrieved = retriever.search(args.question, top_k=args.top_k)
    answer = synthesize_answer(args.question, retrieved)

    if args.as_json:
        print(json.dumps(_answer_payload(answer), indent=2))
        return 0 if answer.found else 2

    print(answer.answer)
    if answer.citations:
        print()
        print("Sources:")
        for citation in answer.citations:
            location = f"{citation.source_path}:{citation.start_line}-{citation.end_line}"
            print(f"[{citation.label}] {location} {citation.heading}")

    if args.show_context:
        print()
        print("Retrieved context:")
        for result in retrieved:
            print(_format_result(result.rank, result.score, result.chunk))

    return 0 if answer.found else 2


def retrieve(args: argparse.Namespace) -> int:
    retriever = _build_retriever(args.corpus, args.exclude)
    results = retriever.search(args.query, top_k=args.top_k)

    if args.as_json:
        payload = [
            {
                "rank": result.rank,
                "score": round(result.score, 6),
                "source_path": result.chunk.source_path,
                "heading": result.chunk.heading,
                "start_line": result.chunk.start_line,
                "end_line": result.chunk.end_line,
                "preview": result.chunk.preview,
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2))
        return 0

    for result in results:
        print(_format_result(result.rank, result.score, result.chunk))
    return 0


def index(args: argparse.Namespace) -> int:
    chunks = build_chunks(load_markdown_documents(args.corpus, excluded_names=set(args.exclude)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "corpus": str(args.corpus.resolve()),
        "chunk_count": len(chunks),
        "chunks": [chunk.to_dict() for chunk in chunks],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(chunks)} chunks to {args.out}")
    return 0


def evaluate(args: argparse.Namespace) -> int:
    retriever = _build_retriever(args.corpus, args.exclude)
    questions = _load_questions(args.questions)
    failures = 0

    for item in questions:
        question = item["question"]
        expected_sources = set(item.get("expected_sources", []))
        should_answer = bool(item.get("should_answer", True))
        answer = synthesize_answer(question, retriever.search(question, top_k=args.top_k))
        retrieved_sources = {result.chunk.source_path for result in answer.retrieved}
        source_hit = not expected_sources or bool(expected_sources & retrieved_sources)
        found_ok = answer.found is should_answer
        ok = source_hit and found_ok
        failures += 0 if ok else 1
        status = "PASS" if ok else "FAIL"
        print(f"{status} {question}")
        print(f"  found={answer.found} expected_found={should_answer} source_hit={source_hit}")

    print()
    print(f"{len(questions) - failures}/{len(questions)} passed")
    return 0 if failures == 0 else 1


def _build_retriever(corpus: Path, excluded_names: list[str]) -> TfIdfRetriever:
    documents = load_markdown_documents(corpus, excluded_names=set(excluded_names))
    chunks = build_chunks(documents)
    if not chunks:
        raise SystemExit(f"No markdown chunks found under {corpus}")
    return TfIdfRetriever.from_chunks(chunks)


def _load_questions(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"Evaluation file not found: {path}")
    questions: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            questions.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
    return questions


def _answer_payload(answer) -> dict[str, object]:
    return {
        "question": answer.question,
        "answer": answer.answer,
        "found": answer.found,
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


def _format_result(rank: int, score: float, chunk) -> str:
    location = f"{chunk.source_path}:{chunk.start_line}-{chunk.end_line}"
    return f"{rank}. score={score:.3f} {location} {chunk.heading}\n   {chunk.preview}"


if __name__ == "__main__":
    sys.exit(main())
