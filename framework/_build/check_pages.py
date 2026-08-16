"""Static acceptance checks for the generated GitHub Pages artifact."""

from __future__ import annotations

import argparse
import json
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

    lab_shell = site / "jupyter" / "lab" / "index.html"
    if not lab_shell.is_file():
        failures.append("missing JupyterLite lab shell")
    else:
        shell_text = lab_shell.read_text(encoding="utf-8")
        if "course-home" not in shell_text:
            failures.append("JupyterLite lab has no course return link")
        if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', shell_text, re.I):
            failures.append("JupyterLite lab is missing viewport")

    lite_config = site / "jupyter" / "jupyter-lite.json"
    if not lite_config.is_file():
        failures.append("missing JupyterLite configuration")
    elif "@jupyterlite/pyodide-kernel-extension" not in lite_config.read_text(encoding="utf-8"):
        failures.append("JupyterLite has no Pyodide Python kernel")

    lab_notebooks = sorted((site / "jupyter" / "files").rglob("*.ipynb"))
    if not lab_notebooks:
        failures.append("JupyterLite contains no notebooks")
    for notebook in lab_notebooks:
        relative = notebook.relative_to(site / "jupyter" / "files")
        rendered = (site / relative).with_suffix(".html")
        if not rendered.is_file():
            failures.append(f"JupyterLite notebook has no rendered HTML pair: {relative}")
        notebook_data = json.loads(notebook.read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook_data.get("cells", [])
            if cell.get("cell_type") == "code"
        )
        if re.search(r"(?m)^!python\s+", source):
            failures.append(f"unsupported shell cell remains in JupyterLite: {relative}")

    unexpected_notebooks = [
        path for path in site.rglob("*.ipynb")
        if ((site / "jupyter" / "files") not in path.parents
            and path.name != "jupyter-lite.ipynb")
    ]
    if unexpected_notebooks:
        failures.append("publication notebooks must only exist inside JupyterLite contents")

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
        if relative.parts[0] == "jupyter":
            continue  # JupyterLite owns and resolves its internal application assets.
        if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', text, re.I):
            failures.append(f"missing viewport: {relative}")
        if relative != Path("index.html") and "course-home" not in text:
            failures.append(f"missing course return link: {relative}")
        if (site / "jupyter" / "files" / relative.with_suffix(".ipynb")).is_file():
            if "course-lab" not in text:
                failures.append(f"rendered notebook has no editable lab link: {relative}")
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
    print(
        f"Pages checks passed: {len(html_files)} HTML files, "
        f"{len(lab_notebooks)} editable notebooks, base {args.base_path}"
    )


if __name__ == "__main__":
    main()
