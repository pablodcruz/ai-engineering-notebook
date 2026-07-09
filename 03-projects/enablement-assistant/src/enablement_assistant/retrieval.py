from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re

from .documents import DocumentChunk


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "the",
    "this",
    "to",
    "what",
    "with",
}


@dataclass(frozen=True)
class RetrievalResult:
    rank: int
    score: float
    chunk: DocumentChunk


class TfIdfRetriever:
    def __init__(
        self,
        chunks: list[DocumentChunk],
        vectors: list[dict[str, float]],
        idf: dict[str, float],
    ) -> None:
        self.chunks = chunks
        self.vectors = vectors
        self.idf = idf

    @classmethod
    def from_chunks(cls, chunks: list[DocumentChunk]) -> "TfIdfRetriever":
        doc_frequencies: Counter[str] = Counter()
        tokenized_chunks: list[list[str]] = []

        for chunk in chunks:
            terms = tokenize(f"{chunk.heading} {chunk.text}")
            tokenized_chunks.append(terms)
            doc_frequencies.update(set(terms))

        total = max(len(chunks), 1)
        idf = {
            term: math.log((1 + total) / (1 + frequency)) + 1
            for term, frequency in doc_frequencies.items()
        }
        vectors = [_normalize(_tfidf_vector(terms, idf)) for terms in tokenized_chunks]
        return cls(chunks=chunks, vectors=vectors, idf=idf)

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        query_terms = tokenize(query)
        query_vector = _normalize(_tfidf_vector(query_terms, self.idf))
        scored: list[tuple[float, DocumentChunk]] = []

        for chunk, vector in zip(self.chunks, self.vectors):
            score = _dot(query_vector, vector)
            score += _phrase_boost(query_terms, chunk)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievalResult(rank=rank, score=score, chunk=chunk)
            for rank, (score, chunk) in enumerate(scored[:top_k], start=1)
        ]


def tokenize(text: str) -> list[str]:
    terms = [match.group(0).lower() for match in TOKEN_RE.finditer(text.lower())]
    return [
        _normalize_token(term)
        for term in terms
        if term not in STOPWORDS and len(term) > 1
    ]


def _tfidf_vector(terms: list[str], idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(terms)
    total = max(sum(counts.values()), 1)
    return {
        term: (count / total) * idf.get(term, 1.0)
        for term, count in counts.items()
    }


def _normalize(vector: dict[str, float]) -> dict[str, float]:
    magnitude = math.sqrt(sum(value * value for value in vector.values()))
    if magnitude == 0:
        return vector
    return {term: value / magnitude for term, value in vector.items()}


def _dot(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(term, 0.0) for term, value in left.items())


def _phrase_boost(query_terms: list[str], chunk: DocumentChunk) -> float:
    if not query_terms:
        return 0.0
    haystack = f"{chunk.heading} {chunk.text}".lower()
    matched = sum(1 for term in set(query_terms) if term in haystack)
    return min(matched * 0.01, 0.05)


def _normalize_token(term: str) -> str:
    if term.startswith("document"):
        return "document"
    if len(term) > 4 and term.endswith("ies"):
        return f"{term[:-3]}y"
    if len(term) > 4 and term.endswith("ing"):
        return term[:-3]
    if len(term) > 4 and term.endswith("ed"):
        return term[:-2]
    if len(term) > 3 and term.endswith("s"):
        return term[:-1]
    return term
