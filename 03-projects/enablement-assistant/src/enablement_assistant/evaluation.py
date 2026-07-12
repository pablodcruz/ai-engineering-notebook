from __future__ import annotations

from pathlib import Path
from typing import Any

from .answer import GroundedAnswer


def evaluate_item(
    item: dict[str, Any],
    answer: GroundedAnswer,
    *,
    corpus_root: Path,
) -> dict[str, Any]:
    should_answer = bool(item.get("should_answer", True))
    expected_sources = [str(value) for value in item.get("expected_sources", [])]
    retrieved_sources = [result.chunk.source_path for result in answer.retrieved]
    cited_sources = [citation.source_path for citation in answer.citations]
    diagnostics: list[str] = []

    checks = {
        "answer_behavior": answer.found is should_answer,
        "retrieval_source": not expected_sources
        or any(source in retrieved_sources for source in expected_sources),
        "citation_contract": _citation_contract_ok(answer, should_answer),
        "citation_precision": _citation_targets_ok(
            item.get("citation_targets", []), answer, corpus_root, diagnostics
        ),
        "answer_traits": _answer_traits_ok(item, answer.answer, diagnostics),
    }

    if not checks["answer_behavior"]:
        diagnostics.append(f"expected found={should_answer}, got found={answer.found}")
    if not checks["retrieval_source"]:
        diagnostics.append(
            f"expected one of {expected_sources} in retrieved sources; got {retrieved_sources}"
        )
    if not checks["citation_contract"]:
        diagnostics.append(
            f"citation contract failed for found={answer.found}; cited sources={cited_sources}"
        )

    max_citations = item.get("max_citations")
    if max_citations is not None:
        checks["citation_count"] = len(answer.citations) <= int(max_citations)
        if not checks["citation_count"]:
            diagnostics.append(
                f"expected at most {max_citations} citations; got {len(answer.citations)}"
            )

    return {
        "id": str(item.get("id", item["question"])),
        "category": str(item.get("category", "uncategorized")),
        "question": str(item["question"]),
        "expected_sources": expected_sources,
        "should_answer": should_answer,
        "found": answer.found,
        "passed": all(checks.values()),
        "checks": checks,
        "diagnostics": diagnostics,
    }


def _citation_contract_ok(answer: GroundedAnswer, should_answer: bool) -> bool:
    if not should_answer:
        return not answer.found and not answer.citations
    if not answer.found or not answer.citations:
        return False
    labels = [citation.label for citation in answer.citations]
    return labels == [f"S{index}" for index in range(1, len(labels) + 1)] and all(
        citation.source_path
        and citation.heading
        and citation.start_line > 0
        and citation.end_line >= citation.start_line
        and f"[{citation.label}]" in answer.answer
        for citation in answer.citations
    )


def _citation_targets_ok(
    targets: list[dict[str, Any]],
    answer: GroundedAnswer,
    corpus_root: Path,
    diagnostics: list[str],
) -> bool:
    if not targets:
        return True

    target_results = []
    for target in targets:
        source = str(target["source"])
        heading = str(target.get("heading_contains", "")).lower()
        evidence = [str(value).lower() for value in target.get("evidence", [])]
        matched = False
        for citation in answer.citations:
            if citation.source_path != source:
                continue
            if heading and heading not in citation.heading.lower():
                continue
            path = corpus_root / citation.source_path
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            if citation.end_line > len(lines):
                continue
            cited_text = "\n".join(lines[citation.start_line - 1 : citation.end_line]).lower()
            if evidence and not all(term in cited_text for term in evidence):
                continue
            matched = True
            break
        target_results.append(matched)

    if any(target_results):
        return True
    diagnostics.append(
        "no citation matched an expected source, heading, and evidence-bearing line range"
    )
    return False


def _answer_traits_ok(item: dict[str, Any], answer: str, diagnostics: list[str]) -> bool:
    lowered = answer.lower()
    required = [str(value).lower() for value in item.get("answer_must_include", [])]
    required_any = [str(value).lower() for value in item.get("answer_must_include_any", [])]
    forbidden = [str(value).lower() for value in item.get("answer_must_not_include", [])]

    missing = [term for term in required if term not in lowered]
    any_missing = bool(required_any) and not any(term in lowered for term in required_any)
    present_forbidden = [term for term in forbidden if term in lowered]
    if missing:
        diagnostics.append(f"answer missing required traits: {missing}")
    if any_missing:
        diagnostics.append(f"answer missing every allowed trait: {required_any}")
    if present_forbidden:
        diagnostics.append(f"answer contains forbidden traits: {present_forbidden}")
    return not missing and not any_missing and not present_forbidden
