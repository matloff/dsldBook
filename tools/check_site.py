#!/usr/bin/env python3
"""Check the rendered book's local links, anchors, images, scripts and fonts."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for attr in ("href", "src", "poster"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def check(root):
    root = root.resolve()
    pages = {path: Page(path) for path in root.glob("*.html")}
    problems = []
    checked = 0

    def check_url(source, url):
        nonlocal checked
        parts = urlsplit(url)
        if parts.scheme or parts.netloc:
            return
        # A bare # is used by Quarto's navigation controls.
        if not parts.path and not parts.fragment:
            return
        path = unquote(parts.path)
        target = ((root / path.lstrip("/")) if path.startswith("/")
                  else (source.parent / path if path else source)).resolve()
        if target.is_dir():
            target /= "index.html"
        checked += 1
        try:
            relative = target.relative_to(root)
        except ValueError:
            problems.append(f"{source.name}: link escapes output directory: {url}")
            return
        current = root
        for component in relative.parts:
            if not current.is_dir() or component not in {p.name for p in current.iterdir()}:
                problems.append(f"{source.name}: missing or case-mismatched resource: {url}")
                return
            current /= component
        if parts.fragment and target.suffix == ".html":
            if target not in pages:
                pages[target] = Page(target)
            if unquote(parts.fragment) not in pages[target].ids:
                problems.append(f"{source.name}: missing anchor: {url}")

    if not pages:
        problems.append("No rendered HTML pages found; run make html first.")
    for path, page in list(pages.items()):
        for anchor, count in Counter(page.ids).items():
            if count > 1:
                problems.append(f"{path.name}: duplicate id: {anchor}")
        for url in page.links:
            check_url(path, url)
        source = path.read_text()
        if 'quarto-xref-unresolved' in source or r"\textemdash" in source:
            problems.append(f"{path.name}: unresolved reference or unsupported em-dash command")
    for path in root.rglob("*.css"):
        for url in re.findall(r"url\(\s*['\"]?([^)'\"]+)", path.read_text()):
            check_url(path, url.strip())
    search = root / "search.json"
    if not search.exists():
        problems.append("Search index is missing.")
    else:
        for entry in json.loads(search.read_text()):
            if entry.get("href"):
                check_url(root / "index.html", entry["href"])
    if problems:
        print("\n".join(sorted(set(problems))))
        return 1
    print(f"PASS: {len(pages)} pages; {checked} local resource/anchor references; search index.")
    return 0


if __name__ == "__main__":
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1 else "docs")))
