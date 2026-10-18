#!/usr/bin/env python3
"""Check the published static artifact, local references and stable entry points."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1] / "website"
PUBLIC_HOST = "khanhvu-ops.github.io"
REQUIRED = (
    "index.html", "privacy.html", "terms.html", "support.html",
    "paper-drift.html", "app-ads.txt", "assets/kv-apps.svg",
)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []
        self.duplicates = set()
        self.feed(text)
        self.close()
        # CSS paint-server fragments are not navigation links; selectors may be unused.
        self.refs += [ref for ref in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", text)
                      if not ref.startswith("#")]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                self.duplicates.add(attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src", "poster"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        for candidate in attrs.get("srcset", "").split(","):
            if candidate.strip():
                self.refs.append(candidate.strip().split()[0])

    handle_startendtag = handle_starttag


def main():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f"Missing stable public file: {name}")
    for name in ("docs", "content", ".git"):
        if (ROOT / name).exists():
            errors.append(f"Non-website directory inside artifact: {name}")

    pages = {p.resolve(): Page(p.read_text(encoding="utf-8")) for p in ROOT.rglob("*.html")}
    count = 0
    for path, page in pages.items():
        label = path.relative_to(ROOT)
        for duplicate in sorted(page.duplicates):
            errors.append(f"{label}: duplicate id #{duplicate}")
        for ref in page.refs:
            url = urlsplit(ref)
            if url.netloc and url.netloc.lower() != PUBLIC_HOST:
                continue
            if url.scheme and url.scheme not in ("http", "https"):
                continue
            if url.scheme in ("http", "https") and not url.netloc:
                continue
            if url.netloc or url.path.startswith("/"):
                target = ROOT / unquote(url.path).lstrip("/")
            elif url.path:
                target = path.parent / unquote(url.path)
            else:
                target = path
            target = target.resolve()
            if not target.is_relative_to(ROOT):
                errors.append(f"{label}: reference leaves website/: {ref}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"{label}: missing target: {ref}")
                continue
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{label}: missing anchor: {ref}")
            count += 1
    sitemap = ROOT / "sitemap.xml"
    if sitemap.is_file():
        listed = set(re.findall(r"<loc>https://" + re.escape(PUBLIC_HOST) + r"/([^<]*)</loc>",
                                sitemap.read_text(encoding="utf-8")))
        for path in pages:
            name = path.relative_to(ROOT).as_posix()
            if (("" if name == "index.html" else name)) not in listed:
                errors.append(f"sitemap.xml: missing page {name}")
        for name in listed:
            if not (ROOT / (name or "index.html")).is_file():
                errors.append(f"sitemap.xml: listed page does not exist: /{name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(pages)} HTML pages, {count} local references, stable public entry points.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
