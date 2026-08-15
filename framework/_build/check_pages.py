"""Static acceptance checks for the generated GitHub Pages artifact."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.urls.append(value)


def local_target(page: Path, raw: str, site: Path, base_path: str) -> Path | None:
    split = urlsplit(raw)
    if split.scheme or split.netloc or raw.startswith(("#", "data:", "mailto:")):
        return None
    path = unquote(split.path)
    if not path:
        return None
    if path.startswith("/"):
        if not path.startswith(base_path):
            raise ValueError(f"root-relative URL escapes Pages base path: {raw}")
        return site / path[len(base_path):]
    return (page.parent / path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", type=Path)
    parser.add_argument("--base-path", default="/algo_trading_intro/")
    args = parser.parse_args()
    site = args.site.resolve()
    failures: list[str] = []
    html_files = sorted(site.rglob("*.html"))
    if not (site / "index.html").is_file():
        failures.append("missing index.html")
    if list(site.rglob("*.ipynb")):
        failures.append("publication artifact must not contain .ipynb sources")

    index = (site / "index.html").read_text(encoding="utf-8")
    for n in range(1, 15):
        for suffix in (f"{n:02d}_build_exercises.html", f"{n:02d}_auxiliary.html"):
            matches = list(site.glob(f"{n:02d}-*/exercises/{suffix}"))
            if len(matches) != 1:
                failures.append(f"expected one rendered notebook: {suffix}")
            elif suffix not in index:
                failures.append(f"index does not link {suffix}")
    if len(re.findall(r'class="lc-actions"', index)) != 14:
        failures.append("index must expose three actions for each of the 14 classes")

    for page in html_files:
        text = page.read_text(encoding="utf-8")
        relative = page.relative_to(site)
        if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', text, re.I):
            failures.append(f"missing viewport: {relative}")
        if relative != Path("index.html") and "course-home" not in text:
            failures.append(f"missing course return link: {relative}")
        parser_links = Links()
        parser_links.feed(text)
        for raw in parser_links.urls:
            try:
                target = local_target(page, raw, site, args.base_path)
            except ValueError as exc:
                failures.append(f"{relative}: {exc}")
                continue
            if target is not None and not target.exists():
                failures.append(f"broken link in {relative}: {raw}")

    if failures:
        print("Pages checks failed:")
        for failure in failures[:50]:
            print(f"- {failure}")
        sys.exit(1)
    print(f"Pages checks passed: {len(html_files)} HTML files, base {args.base_path}")


if __name__ == "__main__":
    main()
