from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .documents import DocumentChunk
from .retrieval import RetrievalResult, tokenize


@dataclass(frozen=True)
class Citation:
    label: str
    source_path: str
    heading: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class GroundedAnswer:
    question: str
    answer: str
    found: bool
    citations: list[Citation]
    retrieved: list[RetrievalResult]


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n{2,}")
REFUSAL_PATTERNS = (
    "ignore the sources",
    "ignore sources",
    "general knowledge instead",
    "reveal private",
    "private notes",
    "reveal secrets",
)


def synthesize_answer(
    question: str,
    retrieved: list[RetrievalResult],
    *,
    min_score: float = 0.06,
    max_sentences: int = 4,
    max_sources: int = 2,
) -> GroundedAnswer:
    """Create a concise extractive answer from retrieved chunks."""
    lowered_question = question.lower()
    if any(pattern in lowered_question for pattern in REFUSAL_PATTERNS):
        return _not_found(question, retrieved)
    if not retrieved or retrieved[0].score < min_score:
        return _not_found(question, retrieved)

    query_terms = set(tokenize(question))
    required_overlap = min(len(query_terms), max(2, math.ceil(len(query_terms) * 0.5)))
    best_overlap = max(
        (
            len(query_terms & set(tokenize(f"{result.chunk.heading} {result.chunk.text}")))
            for result in retrieved
        ),
        default=0,
    )
    if best_overlap < required_overlap:
        return _not_found(question, retrieved)

    sentence_candidates: list[tuple[float, str, DocumentChunk]] = []

    for result in retrieved:
        if result.score < min_score:
            continue
        for sentence in _split_sentences(result.chunk.text):
            sentence_terms = set(tokenize(f"{result.chunk.heading} {sentence}"))
            overlap = len(query_terms & sentence_terms)
            if overlap < required_overlap:
                continue
            sentence_score = result.score + (overlap / max(len(query_terms), 1))
            sentence_candidates.append((sentence_score, sentence.strip(), result.chunk))

    if not sentence_candidates:
        return _not_found(question, retrieved)

    sentence_candidates.sort(key=lambda item: item[0], reverse=True)
    selected: list[tuple[str, DocumentChunk]] = []
    seen_sentences: set[str] = set()
    seen_sources: dict[str, str] = {}

    for _, sentence, chunk in sentence_candidates:
        normalized = " ".join(sentence.lower().split())
        if normalized in seen_sentences:
            continue
        source_key = chunk.source_key
        if source_key not in seen_sources and len(seen_sources) >= max_sources:
            continue
        if source_key not in seen_sources:
            seen_sources[source_key] = f"S{len(seen_sources) + 1}"
        selected.append((sentence, chunk))
        seen_sentences.add(normalized)
        if len(selected) >= max_sentences:
            break

    if not selected:
        return _not_found(question, retrieved)

    answer_parts: list[str] = []
    for sentence, chunk in selected:
        label = seen_sources[chunk.source_key]
        answer_parts.append(f"{sentence} [{label}]")

    citations = [
        Citation(
            label=label,
            source_path=source_key.split("::", maxsplit=1)[0],
            heading=source_key.split("::", maxsplit=1)[1],
            start_line=_first_chunk_for_source(source_key, selected).start_line,
            end_line=_first_chunk_for_source(source_key, selected).end_line,
        )
        for source_key, label in seen_sources.items()
    ]

    return GroundedAnswer(
        question=question,
        answer=" ".join(answer_parts),
        found=True,
        citations=citations,
        retrieved=retrieved,
    )


def _not_found(question: str, retrieved: list[RetrievalResult]) -> GroundedAnswer:
    return GroundedAnswer(
        question=question,
        answer="I could not find this in the indexed sources.",
        found=False,
        citations=[],
        retrieved=retrieved,
    )


def _split_sentences(text: str) -> list[str]:
    sentences = [part.strip(" -\t\r\n") for part in SENTENCE_RE.split(text)]
    return [
        sentence
        for sentence in sentences
        if len(sentence.split()) >= 2 and set(sentence) != {"|", "-", " "}
    ]


def _first_chunk_for_source(
    source_key: str, selected: list[tuple[str, DocumentChunk]]
) -> DocumentChunk:
    for _, chunk in selected:
        if chunk.source_key == source_key:
            return chunk
    raise ValueError(f"Missing selected chunk for source {source_key}")
