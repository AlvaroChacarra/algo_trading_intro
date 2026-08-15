"""Build the static GitHub Pages site without changing generated course sources."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import warnings
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat
from nbconvert import HTMLExporter
from nbformat.validator import normalize
from nbformat.warnings import MissingIDFieldWarning


ROOT = Path(__file__).resolve().parents[2]
SKIP_PARTS = {".git", ".github", "_site", "node_modules", "__pycache__"}
ASSET_SUFFIXES = {
    ".css", ".js", ".json", ".csv", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".otf", ".wasm",
}

MOBILE_CSS = r"""
<style id="pages-mobile">
  html { overflow-wrap: break-word; }
  body { max-width: 100%; }
  pre { max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
  table { max-width: 100%; }
  img, video { max-width: 100%; height: auto; }
  canvas, svg { max-width: 100%; }
  .course-home {
    position: fixed; left: max(12px, env(safe-area-inset-left));
    bottom: max(12px, env(safe-area-inset-bottom)); z-index: 10000;
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 44px; padding: 0 14px; border: 1px solid rgba(34,211,238,.55);
    border-radius: 999px; background: rgba(9,9,11,.94); color: #22d3ee;
    box-shadow: 0 5px 20px rgba(0,0,0,.35); text-decoration: none;
    font: 600 13px/1 system-ui,-apple-system,sans-serif;
  }
  @media (max-width: 700px) {
    .jp-Notebook { padding: 12px 8px 78px !important; }
    .jp-Cell { margin-left: 0 !important; margin-right: 0 !important; }
    .jp-RenderedHTMLCommon { padding-left: 8px !important; padding-right: 8px !important; }
    .jp-RenderedHTMLCommon table { display: block; overflow-x: auto;
      -webkit-overflow-scrolling: touch; }
    .jp-OutputArea-output { max-width: 100%; overflow-x: auto; }
    .jp-CodeCell .jp-Cell-inputWrapper, .jp-CodeCell .jp-Cell-outputWrapper {
      max-width: 100%; overflow-x: auto;
    }
  }
</style>
"""


def _skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)


def _safe_output(path: Path) -> Path:
    output = path.resolve()
    if output in {ROOT, Path("/")}:
        raise ValueError(f"unsafe output directory: {output}")
    return output


def _home_href(destination: Path, output: Path) -> str:
    return os.path.relpath(output / "index.html", destination.parent).replace(os.sep, "/")


def augment_html(document: str, home_href: str | None) -> str:
    """Add publication-only mobile safeguards and a persistent course link."""
    head_bits = MOBILE_CSS
    if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', document, re.I):
        head_bits = '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head_bits
    document, count = re.subn(r"</head\s*>", head_bits + "</head>", document,
                              count=1, flags=re.I)
    if count != 1:
        raise ValueError("HTML document has no closing </head>")
    if home_href:
        link = (f'<a class="course-home" href="{html.escape(home_href, quote=True)}" '
                'aria-label="Volver al índice del curso">← Curso</a>')
        document, count = re.subn(r"(<body\b[^>]*>)", r"\1\n" + link,
                                  document, count=1, flags=re.I)
        if count != 1:
            raise ValueError("HTML document has no <body>")
    return document


def _copy_html_and_assets(output: Path) -> list[Path]:
    copied_html: list[Path] = []
    for source in ROOT.rglob("*"):
        if not source.is_file() or _skipped(source):
            continue
        relative = source.relative_to(ROOT)
        if "framework" in relative.parts:
            continue
        if relative.match("15-final-exam/examen_*.html"):
            continue  # never publish the generated answer key
        destination = output / relative
        if source.suffix.lower() == ".html":
            destination.parent.mkdir(parents=True, exist_ok=True)
            home = None if relative == Path("index.html") else _home_href(destination, output)
            destination.write_text(augment_html(source.read_text(encoding="utf-8"), home),
                                   encoding="utf-8")
            copied_html.append(destination)
        elif source.suffix.lower() in ASSET_SUFFIXES:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return copied_html


def _copy_local_html_targets(output: Path, html_files: list[Path]) -> None:
    """Keep non-HTML files explicitly linked by a published HTML page."""
    pattern = re.compile(r'(?:href|src)=["\']([^"\']+)["\']', re.I)
    for published in html_files:
        for raw in pattern.findall(published.read_text(encoding="utf-8")):
            split = urlsplit(raw)
            if split.scheme or split.netloc or raw.startswith(("#", "data:")):
                continue
            target = (published.parent / unquote(split.path)).resolve()
            try:
                relative = target.relative_to(output)
            except ValueError:
                continue
            source = ROOT / relative
            if source.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


def _convert_notebooks(output: Path) -> list[Path]:
    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    converted: list[Path] = []
    for source in sorted(ROOT.rglob("*.ipynb")):
        if _skipped(source) or "framework" in source.relative_to(ROOT).parts:
            continue
        relative = source.relative_to(ROOT).with_suffix(".html")
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", MissingIDFieldWarning)
            notebook = nbformat.read(source, as_version=4)
            _, notebook = normalize(notebook)
        rendered, resources = exporter.from_notebook_node(
            notebook, resources={"metadata": {"name": source.stem}}
        )
        destination.write_text(
            augment_html(rendered, _home_href(destination, output)), encoding="utf-8"
        )
        for name, payload in resources.get("outputs", {}).items():
            asset = destination.parent / name
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_bytes(payload)
        converted.append(destination)
    return converted


def build(output: Path) -> tuple[int, int]:
    output = _safe_output(output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    html_files = _copy_html_and_assets(output)
    _copy_local_html_targets(output, html_files)
    notebooks = _convert_notebooks(output)
    (output / ".nojekyll").touch()
    return len(html_files), len(notebooks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    html_count, notebook_count = build(args.output)
    print(f"Pages site ready: {html_count} source HTML + {notebook_count} notebooks")


if __name__ == "__main__":
    main()
