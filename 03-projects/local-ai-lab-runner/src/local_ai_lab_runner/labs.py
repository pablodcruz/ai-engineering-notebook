from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class LabDocument:
    path: Path
    relative_path: str
    text: str
    title: str
    sections: tuple[str, ...]

    def has_section(self, name: str) -> bool:
        normalized = normalize_heading(name)
        return any(normalize_heading(section) == normalized for section in self.sections)


def load_lab(path: Path, *, root: Path | None = None) -> LabDocument:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Lab file not found: {path}")
    if resolved.suffix.lower() != ".md":
        raise ValueError(f"Lab file must be markdown: {path}")

    text = resolved.read_text(encoding="utf-8")
    headings = parse_headings(text)
    title = next((heading for level, heading in headings if level == 1), "")
    sections = tuple(heading for level, heading in headings if level == 2)
    relative_path = _relative_path(resolved, root)
    return LabDocument(
        path=resolved, relative_path=relative_path, text=text, title=title, sections=sections
    )


def discover_labs(root: Path) -> list[Path]:
    resolved = root.resolve()
    return sorted(
        path
        for path in resolved.glob("*.md")
        if path.name != "lab-template.md" and path.name.lower() != "readme.md"
    )


def parse_headings(text: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip()))
    return headings


def normalize_heading(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _relative_path(path: Path, root: Path | None) -> str:
    if root is None:
        return path.name
    try:
        return path.relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name
