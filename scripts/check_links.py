from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "playwright-report",
    "test-results",
    "coverage",
}
DOC_EXTENSIONS = {".md", ".html"}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


@dataclass(frozen=True)
class Link:
    source: Path
    target: str


class LinkParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__()
        self.source = source
        self.links: list[Link] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(Link(source=self.source, target=value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local documentation links.")
    parser.add_argument(
        "--external-domain",
        action="append",
        default=[],
        help="Also check HTTP(S) links for this domain. May be passed more than once.",
    )
    parser.add_argument(
        "--site-base-url",
        action="append",
        default=[],
        help="Map links under this deployed site URL back to local repository paths.",
    )
    args = parser.parse_args()

    external_domains = set(args.external_domain)
    site_base_urls = [base.rstrip("/") + "/" for base in args.site_base_url]
    failures = []

    for link in collect_links():
        failure = check_link(link, external_domains, site_base_urls)
        if failure:
            failures.append(failure)

    if failures:
        print("Broken links found:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("All documentation links passed.")
    return 0


def collect_links() -> list[Link]:
    links: list[Link] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DOC_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".md":
            links.extend(
                Link(source=path, target=match.group(1))
                for match in MARKDOWN_LINK_RE.finditer(text)
            )
        elif path.suffix.lower() == ".html":
            html_parser = LinkParser(path)
            html_parser.feed(text)
            links.extend(html_parser.links)
    return links


def check_link(link: Link, external_domains: set[str], site_base_urls: list[str]) -> str | None:
    target = link.target.strip()
    if should_skip(target):
        return None

    parsed = urlparse(target)
    if parsed.scheme in {"http", "https"}:
        for base_url in site_base_urls:
            if target.startswith(base_url):
                mapped_path = target.removeprefix(base_url).split("#", maxsplit=1)[0]
                return check_local_path(link, mapped_path, target, base_dir=ROOT)
        if parsed.netloc not in external_domains:
            return None
        return check_external(link, target)

    return check_local_path(link, parsed.path, target)


def check_local_path(
    link: Link,
    target_path: str,
    original_target: str,
    *,
    base_dir: Path | None = None,
) -> str | None:
    if not target_path:
        return None

    if target_path.startswith("/"):
        candidate = ROOT / target_path.lstrip("/")
    else:
        candidate = (base_dir or link.source.parent) / unquote(target_path)

    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return f"{relative(link.source)} links outside repository: {original_target}"

    if not candidate.exists():
        return f"{relative(link.source)} has missing target: {original_target}"
    return None


def check_external(link: Link, target: str) -> str | None:
    request = Request(
        target, method="HEAD", headers={"User-Agent": "ai-engineering-notebook-link-check"}
    )
    try:
        with urlopen(request, timeout=15) as response:
            if response.status >= 400:
                return f"{relative(link.source)} has HTTP {response.status}: {target}"
            return None
    except HTTPError as error:
        if error.code == 405:
            return check_external_get(link, target)
        return f"{relative(link.source)} has HTTP {error.code}: {target}"
    except URLError as error:
        return f"{relative(link.source)} could not reach {target}: {error.reason}"


def check_external_get(link: Link, target: str) -> str | None:
    request = Request(
        target, method="GET", headers={"User-Agent": "ai-engineering-notebook-link-check"}
    )
    try:
        with urlopen(request, timeout=15) as response:
            if response.status >= 400:
                return f"{relative(link.source)} has HTTP {response.status}: {target}"
            return None
    except HTTPError as error:
        return f"{relative(link.source)} has HTTP {error.code}: {target}"
    except URLError as error:
        return f"{relative(link.source)} could not reach {target}: {error.reason}"


def should_skip(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or target.startswith("mailto:")
        or target.startswith("javascript:")
        or target.startswith("data:")
        or target.startswith("file:")
    )


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
