from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TypedDict

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DEFAULT_EXCLUDES = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}


class Section(TypedDict):
    heading: str
    body: list[tuple[int, str]]


@dataclass(frozen=True)
class MarkdownDocument:
    path: Path
    relative_path: str
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    source_path: str
    heading: str
    start_line: int
    end_line: int
    text: str

    @property
    def source_key(self) -> str:
        return f"{self.source_path}::{self.heading}"

    @property
    def preview(self) -> str:
        compact = " ".join(self.text.split())
        return compact[:220] + ("..." if len(compact) > 220 else "")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_markdown_documents(
    root: Path,
    *,
    excluded_names: set[str] | None = None,
) -> list[MarkdownDocument]:
    excluded = DEFAULT_EXCLUDES | (excluded_names or set())
    root = root.resolve()
    documents: list[MarkdownDocument] = []

    for path in sorted(root.rglob("*.md")):
        if any(part in excluded for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8")
        relative_path = path.relative_to(root).as_posix()
        documents.append(MarkdownDocument(path=path, relative_path=relative_path, text=text))

    return documents


def build_chunks(
    documents: list[MarkdownDocument],
    *,
    target_words: int = 180,
    overlap_words: int = 35,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(
            _chunk_document(document, target_words=target_words, overlap_words=overlap_words)
        )
    return chunks


def _chunk_document(
    document: MarkdownDocument,
    *,
    target_words: int,
    overlap_words: int,
) -> list[DocumentChunk]:
    sections = _sections(document.text)
    chunks: list[DocumentChunk] = []

    for section_index, section in enumerate(sections):
        words = _words_with_lines(section["body"])
        if not words:
            continue

        start = 0
        chunk_index = 0
        while start < len(words):
            end = min(start + target_words, len(words))
            chunk_words = words[start:end]
            start_line = min(line for _, line in chunk_words)
            end_line = max(line for _, line in chunk_words)
            chunk_text = _text_from_words(chunk_words)
            chunk_id = (
                f"{document.relative_path}#section-{section_index + 1}-chunk-{chunk_index + 1}"
            )
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    source_path=document.relative_path,
                    heading=str(section["heading"]),
                    start_line=start_line,
                    end_line=end_line,
                    text=chunk_text,
                )
            )
            if end == len(words):
                break
            start = max(end - overlap_words, start + 1)
            chunk_index += 1

    return chunks


def _sections(text: str) -> list[Section]:
    lines = text.splitlines()
    sections: list[Section] = []
    heading_stack: list[tuple[int, str]] = []
    current_heading = "Document"
    current_body: list[tuple[int, str]] = []

    def flush() -> None:
        nonlocal current_body
        if current_body:
            sections.append({"heading": current_heading, "body": current_body})
            current_body = []

    for line_number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            flush()
            level = len(match.group(1))
            title = match.group(2).strip()
            heading_stack[:] = [
                (existing_level, existing_title)
                for existing_level, existing_title in heading_stack
                if existing_level < level
            ]
            heading_stack.append((level, title))
            current_heading = " > ".join(title for _, title in heading_stack)
            continue
        current_body.append((line_number, line))

    flush()
    return sections


def _words_with_lines(lines: list[tuple[int, str]]) -> list[tuple[str, int]]:
    words: list[tuple[str, int]] = []
    for line_number, line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        for word in stripped.split():
            words.append((word, line_number))
    return words


def _text_from_words(words: list[tuple[str, int]]) -> str:
    grouped_lines: list[str] = []
    current_line_number: int | None = None
    current_words: list[str] = []

    for word, line_number in words:
        if current_line_number is None:
            current_line_number = line_number
        if line_number != current_line_number:
            grouped_lines.append(" ".join(current_words))
            current_words = []
            current_line_number = line_number
        current_words.append(word)

    if current_words:
        grouped_lines.append(" ".join(current_words))

    return "\n".join(grouped_lines)
