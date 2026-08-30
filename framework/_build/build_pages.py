"""Build the static GitHub Pages site without changing generated course sources."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import uuid
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, unquote, urlsplit

import nbformat
from nbconvert import HTMLExporter
from nbformat.validator import normalize
from nbformat.warnings import MissingIDFieldWarning

_BUILD_HELPER_DIR = Path(__file__).resolve().parent
if str(_BUILD_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_BUILD_HELPER_DIR))
from pages_offline_policy import (  # noqa: E402
    harden_service_worker,
    inject_offline_csp,
    validate_hardened_service_worker,
    validate_offline_html,
)


ROOT = Path(__file__).resolve().parents[2]
LAB_CONTENT_SUFFIXES = {".ipynb", ".py", ".csv", ".json", ".md", ".txt"}
PUBLIC_MANIFEST = Path(__file__).with_name("pages_public_manifest.json")
OUTPUT_OWNER_FILE = ".pages-build-owned.json"
OUTPUT_INTEGRITY_FILE = ".pages-integrity.json"
OUTPUT_OWNER = {"schema": 1, "owner": "algo-trading-build-pages"}
JUPYTERLITE_CANONICAL_TIMESTAMP = "1980-01-01T00:00:00.000000Z"
BUILD_INPUT_PATHS = (
    Path("framework/_build/build_pages.py"),
    Path("framework/_build/pages_offline_policy.py"),
    Path("framework/_build/pages_public_manifest.json"),
    Path("package-lock.json"),
    Path("requirements-pages-lock.txt"),
)
GITHUB_SHA_RE = re.compile(r"[0-9a-f]{40}")
PYODIDE_VERSION = "314.0.1"
PYODIDE_ARCHIVE = f"pyodide-core-{PYODIDE_VERSION}.tar.bz2"
PYODIDE_ARCHIVE_URL = (
    "https://github.com/pyodide/pyodide/releases/download/"
    f"{PYODIDE_VERSION}/{PYODIDE_ARCHIVE}"
)
PYODIDE_ARCHIVE_SHA256 = "7220ae5c13993e669559c11ebb236f19b9a143feb18107420b3a49234f06fa67"
PYODIDE_CORE_FILE_NAMES = frozenset({
    "ffi.d.ts",
    "package.json",
    "pyodide-lock.json",
    "pyodide.asm.mjs",
    "pyodide.asm.wasm",
    "pyodide.d.ts",
    "pyodide.js",
    "pyodide.mjs",
    "python",
    "python.bat",
    "python.exe",
    "python_cli_entry.mjs",
    "python_stdlib.zip",
})


def _assert_offline_html(document: str, label: str) -> None:
    validate_offline_html(document, label)


def _strip_disabled_exporter_scripts(document: str) -> str:
    """Remove disabled CDN loaders emitted unconditionally by nbconvert."""
    document = re.sub(
        r"<script\b[^>]*\bsrc=(['\"])\1[^>]*>\s*</script>\s*",
        "",
        document,
        flags=re.I,
    )
    marker = "do not load mermaidjs if not needed"
    lowered = document.lower()
    marker_at = lowered.find(marker)
    if marker_at >= 0:
        start = lowered.rfind("<script", 0, marker_at)
        end = lowered.find("</script>", marker_at)
        if start < 0 or end < 0 or "type=\"module\"" not in lowered[start:marker_at]:
            raise RuntimeError("nbconvert Mermaid loader has an unexpected shape")
        document = document[:start] + document[end + len("</script>"):]
    return document


def _assign_deterministic_cell_ids(notebook: object, relative: Path) -> None:
    cells = notebook.get("cells", []) if isinstance(notebook, dict) else []
    for index, cell in enumerate(cells):
        if isinstance(cell, dict):
            identity = f"{relative.as_posix()}:{index}".encode("utf-8")
            cell["id"] = hashlib.sha256(identity).hexdigest()[:16]


def _canonicalize_jupyterlite_content_metadata(jupyter: Path) -> int:
    """Remove build-clock entropy from JupyterLite's static contents API."""
    api_files = sorted((jupyter / "api" / "contents").glob("**/all.json"))
    if not api_files:
        raise RuntimeError("JupyterLite generated no static contents metadata")

    def normalize_timestamps(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"created", "last_modified"}:
                    value[key] = JUPYTERLITE_CANONICAL_TIMESTAMP
                else:
                    normalize_timestamps(item)
        elif isinstance(value, list):
            for item in value:
                normalize_timestamps(item)

    for path in api_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        normalize_timestamps(data)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return len(api_files)


def _pyodide_kernel_extension() -> Path:
    """Resolve the exact installed JupyterLite Python kernel extension.

    JupyterLite 0.8 auto-discovers federated extensions from ``sys.prefix``.
    The Python package is pinned by ``requirements-pages.txt``; fail closed if
    its matching frontend cannot be found instead of publishing a lab with no
    Python kernel.  Do not also pass the discovered extension through
    ``LiteBuildConfig.federated_extensions``: that registers the same build
    task twice.
    """
    try:
        expected_version = version("jupyterlite-pyodide-kernel")
    except PackageNotFoundError as exc:
        raise RuntimeError("jupyterlite-pyodide-kernel is not installed") from exc
    extension = (
        Path(sys.prefix) / "share" / "jupyter" / "labextensions"
        / "@jupyterlite" / "pyodide-kernel-extension"
    )
    package = extension / "package.json"
    if not package.is_file():
        raise RuntimeError(
            "matching @jupyterlite/pyodide-kernel-extension "
            f"{expected_version} was not found under sys.prefix"
        )
    metadata = json.loads(package.read_text(encoding="utf-8"))
    if (metadata.get("name") != "@jupyterlite/pyodide-kernel-extension"
            or metadata.get("version") != expected_version):
        raise RuntimeError(
            "matching @jupyterlite/pyodide-kernel-extension "
            f"{expected_version} was not found under sys.prefix"
        )
    return extension.resolve()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pyodide_archive() -> Path:
    """Return an integrity-checked Pyodide archive for a network-free lab.

    ``WORK2_PYODIDE_ARCHIVE`` lets CI or a developer supply an already cached
    archive. Otherwise the immutable release asset is downloaded once into a
    task-specific temporary cache. A wrong digest always fails closed.
    """
    supplied = os.environ.get("WORK2_PYODIDE_ARCHIVE")
    if supplied:
        archive = Path(supplied).expanduser().resolve()
        if not archive.is_file():
            raise RuntimeError(f"WORK2_PYODIDE_ARCHIVE does not exist: {archive}")
        if _sha256(archive) != PYODIDE_ARCHIVE_SHA256:
            raise RuntimeError("WORK2_PYODIDE_ARCHIVE failed its SHA-256 check")
        return archive

    cache = Path(tempfile.gettempdir()) / "algo-trading-pages-cache"
    if cache.exists():
        if (cache.is_symlink() or not cache.is_dir()
                or cache.resolve().parent != Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError(f"unsafe Pyodide cache directory: {cache}")
    else:
        cache.mkdir(mode=0o700, parents=False)
    archive = cache / PYODIDE_ARCHIVE
    if archive.is_file():
        if archive.is_symlink():
            raise RuntimeError(f"unsafe cached Pyodide archive: {archive}")
        if _sha256(archive) == PYODIDE_ARCHIVE_SHA256:
            return archive
        archive.unlink()
    elif archive.exists() or archive.is_symlink():
        raise RuntimeError(f"unsafe cached Pyodide archive: {archive}")

    partial = cache / f".{PYODIDE_ARCHIVE}.{uuid.uuid4().hex}.partial"
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(partial, flags, 0o600)
        with os.fdopen(descriptor, "wb") as destination:
            with urllib.request.urlopen(PYODIDE_ARCHIVE_URL, timeout=90) as response:
                shutil.copyfileobj(response, destination)
        if _sha256(partial) != PYODIDE_ARCHIVE_SHA256:
            raise RuntimeError("downloaded Pyodide archive failed its SHA-256 check")
        partial.replace(archive)
    finally:
        partial.unlink(missing_ok=True)
    return archive

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
  .course-lab {
    position: fixed; right: max(12px, env(safe-area-inset-right));
    bottom: max(12px, env(safe-area-inset-bottom)); z-index: 10000;
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 44px; padding: 0 14px; border: 1px solid rgba(74,222,128,.6);
    border-radius: 999px; background: rgba(9,9,11,.94); color: #4ade80;
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

JUPYTERLITE_SHELL_CSS = r"""
<style id="course-navigation">
  .course-home {
    position: fixed; left: max(12px, env(safe-area-inset-left));
    bottom: max(12px, env(safe-area-inset-bottom)); z-index: 10000;
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 44px; padding: 0 14px; border: 1px solid rgba(34,211,238,.65);
    border-radius: 999px; background: rgba(9,9,11,.94); color: #22d3ee;
    box-shadow: 0 5px 20px rgba(0,0,0,.35); text-decoration: none;
    font: 600 13px/1 system-ui,-apple-system,sans-serif;
  }
  @media (max-width: 700px) {
    .jp-NotebookPanel-toolbar { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .jp-Notebook { padding: 12px 6px 76px !important; }
    .jp-Cell { margin-left: 0 !important; margin-right: 0 !important; }
    .jp-CodeCell .jp-Cell-inputWrapper, .jp-CodeCell .jp-Cell-outputWrapper,
    .jp-OutputArea-output { max-width: 100%; overflow-x: auto; }
    .jp-RenderedHTMLCommon table { display: block; max-width: 100%; overflow-x: auto;
      -webkit-overflow-scrolling: touch; }
    .cm-editor .cm-content { font-size: 16px; line-height: 1.45; }
  }
</style>
"""


def _manifest_relative(raw: object) -> Path:
    """Parse one canonical POSIX path without accepting traversal aliases."""
    if not isinstance(raw, str) or not raw:
        raise RuntimeError(f"invalid public manifest path: {raw!r}")
    if "\\" in raw or ":" in raw or any(ord(character) < 32 for character in raw):
        raise RuntimeError(f"non-canonical public manifest path: {raw!r}")
    pure = PurePosixPath(raw)
    if (pure.is_absolute() or pure.as_posix() != raw
            or any(part in {"", ".", ".."} for part in pure.parts)):
        raise RuntimeError(f"non-canonical public manifest path: {raw!r}")
    return Path(*pure.parts)


def _source_file(relative: Path) -> Path:
    """Resolve a declared source and reject symlinks in every path component."""
    candidate = ROOT
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise RuntimeError(f"public source must not be a symlink: {relative.as_posix()}")
    if not candidate.is_file():
        raise RuntimeError(f"declared public source is missing: {relative.as_posix()}")
    return candidate


def _validate_projection_destinations(
    static_files: list[Path], lab_files: list[Path], notebooks: list[Path]
) -> None:
    """Reject aliases that could overwrite or shadow another public output."""
    reserved = {".nojekyll", OUTPUT_OWNER_FILE, OUTPUT_INTEGRITY_FILE}
    static_outputs = [path.as_posix() for path in static_files]
    notebook_outputs = [path.with_suffix(".html").as_posix() for path in notebooks]
    public_outputs = static_outputs + notebook_outputs
    if (any(path in reserved or path.startswith("jupyter/") for path in static_outputs)
            or len({path.casefold() for path in public_outputs}) != len(public_outputs)
            or len({path.as_posix().casefold() for path in lab_files}) != len(lab_files)):
        raise RuntimeError("public manifest contains reserved, colliding, or case-ambiguous destinations")


def _load_public_manifest(manifest_path: Path | None = None) -> dict[str, object]:
    """Load and validate the exact, closed-world publication input set."""
    manifest_path = PUBLIC_MANIFEST if manifest_path is None else manifest_path
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError(f"public manifest is missing or is a symlink: {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid public manifest: {exc}") from exc
    if set(data) != {"schema", "pyodide", "static_files", "lab_files"}:
        raise RuntimeError("public manifest has unexpected or missing top-level fields")
    if data["schema"] != 1:
        raise RuntimeError("unsupported public manifest schema")
    pyodide = data["pyodide"]
    if (not isinstance(pyodide, dict)
            or set(pyodide) != {"version", "archive", "archive_sha256", "core_files"}
            or pyodide.get("version") != PYODIDE_VERSION
            or pyodide.get("archive") != PYODIDE_ARCHIVE
            or pyodide.get("archive_sha256") != PYODIDE_ARCHIVE_SHA256):
        raise RuntimeError("public manifest Pyodide identity does not match the pinned runtime")
    core_files = pyodide["core_files"]
    if (not isinstance(core_files, dict)
            or set(core_files) != PYODIDE_CORE_FILE_NAMES
            or list(core_files) != sorted(core_files)
            or any(not isinstance(digest, str)
                   or not re.fullmatch(r"[0-9a-f]{64}", digest)
                   for digest in core_files.values())):
        raise RuntimeError("public manifest Pyodide core hash map is malformed")
    expected_pyodide = {
        "version": PYODIDE_VERSION,
        "archive": PYODIDE_ARCHIVE,
        "archive_sha256": PYODIDE_ARCHIVE_SHA256,
        "core_files": dict(core_files),
    }

    parsed: dict[str, object] = {
        "schema": 1,
        "pyodide": expected_pyodide,
        "manifest_path": manifest_path,
    }
    for field in ("static_files", "lab_files"):
        raw_paths = data[field]
        if not isinstance(raw_paths, list):
            raise RuntimeError(f"public manifest {field} must be a list")
        paths = [_manifest_relative(raw) for raw in raw_paths]
        identities = [path.as_posix() for path in paths]
        if len(identities) != len(set(identities)) or identities != sorted(identities):
            raise RuntimeError(f"public manifest {field} must be sorted and unique")
        for relative in paths:
            _source_file(relative)
        parsed[field] = paths

    static_files = parsed["static_files"]
    lab_files = parsed["lab_files"]
    assert isinstance(static_files, list) and isinstance(lab_files, list)
    # A declared source may intentionally feed both the rendered static site
    # and JupyterLite (for example a lesson-local CSV).  Each projection is
    # independently closed-world; overlap between them is therefore valid.
    if Path("index.html") not in static_files:
        raise RuntimeError("public manifest must declare index.html")
    if any(path.suffix.lower() not in LAB_CONTENT_SUFFIXES for path in lab_files):
        raise RuntimeError("public manifest lab_files contains an unsupported suffix")
    notebooks = [path for path in lab_files if path.suffix.lower() == ".ipynb"]
    if len(notebooks) != 28:
        raise RuntimeError(f"public manifest must declare exactly 28 core notebooks, found {len(notebooks)}")
    parsed["notebooks"] = notebooks
    _validate_projection_destinations(static_files, lab_files, notebooks)
    return parsed


def _publishable_source(relative: Path) -> bool:
    """Return whether a source is in either exact manifest allowlist."""
    manifest = _load_public_manifest()
    return relative in set(manifest["static_files"]) | set(manifest["lab_files"])


def _safe_output(path: Path) -> Path:
    """Allow only dedicated direct children of ROOT and never follow a symlink."""
    output = Path(os.path.abspath(path.expanduser()))
    safe_name = output.name == "_site" or bool(
        re.fullmatch(r"_site-[A-Za-z0-9][A-Za-z0-9._-]*", output.name)
    )
    if output.parent != ROOT or not safe_name or output.is_symlink():
        raise ValueError(
            f"unsafe output directory (expected ROOT/_site or ROOT/_site-<name>): {output}"
        )
    if output.resolve(strict=False) != output:
        raise ValueError(f"unsafe output directory contains a symlink: {output}")
    return output


def _owned_output(path: Path) -> bool:
    marker = path / OUTPUT_OWNER_FILE
    if marker.is_symlink() or not marker.is_file():
        return False
    try:
        return json.loads(marker.read_text(encoding="utf-8")) == OUTPUT_OWNER
    except (OSError, json.JSONDecodeError):
        return False


def _validate_replacement_target(output: Path) -> None:
    if not output.exists():
        return
    if output.is_symlink() or not output.is_dir() or not _owned_output(output):
        raise RuntimeError(
            f"refusing to replace unowned output directory (missing valid {OUTPUT_OWNER_FILE}): {output}"
        )


def _promote_output(staging: Path, output: Path) -> None:
    """Replace an owned output with rollback; the old site survives build failures."""
    if not output.exists():
        os.replace(staging, output)
        return
    _validate_replacement_target(output)
    backup = ROOT / f".{output.name}.backup-{uuid.uuid4().hex}"
    os.replace(output, backup)
    try:
        os.replace(staging, output)
    except BaseException:
        os.replace(backup, output)
        raise
    if not _owned_output(backup):
        raise RuntimeError(f"refusing to clean unowned backup: {backup}")
    try:
        shutil.rmtree(backup)
    except OSError as exc:
        warnings.warn(
            f"new Pages output is valid but owned backup cleanup failed; preserved {backup}: {exc}",
            RuntimeWarning,
        )


def _home_href(destination: Path, output: Path) -> str:
    return os.path.relpath(output / "index.html", destination.parent).replace(os.sep, "/")


def _lab_href(source: Path, destination: Path, output: Path) -> str:
    app = output / "jupyter" / "lab" / "index.html"
    relative_app = os.path.relpath(app, destination.parent).replace(os.sep, "/")
    notebook_path = quote(source.relative_to(ROOT).as_posix(), safe="/")
    return f"{relative_app}?path={notebook_path}&mode=single-document"


def augment_html(document: str, home_href: str | None,
                 lab_href: str | None = None) -> str:
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
    if lab_href:
        link = (f'<a class="course-lab" href="{html.escape(lab_href, quote=True)}" '
                'target="_blank" rel="noopener" '
                'aria-label="Editar y ejecutar este notebook en el navegador">▶ Ejecutar</a>')
        document, count = re.subn(r"(<body\b[^>]*>)", r"\1\n" + link,
                                  document, count=1, flags=re.I)
        if count != 1:
            raise ValueError("HTML document has no <body>")
    return document


def augment_jupyterlite_shell(document: str, home_href: str) -> str:
    """Add a course return link without disturbing JupyterLab's own styles."""
    document = re.sub(
        r"<title>.*?</title>",
        "<title>Algo Trading · Laboratorio</title>",
        document,
        count=1,
        flags=re.I | re.S,
    )
    document, count = re.subn(r"</head\s*>", JUPYTERLITE_SHELL_CSS + "</head>",
                              document, count=1, flags=re.I)
    if count != 1:
        raise ValueError("JupyterLite shell has no closing </head>")
    link = (f'<a class="course-home" href="{html.escape(home_href, quote=True)}" '
            'aria-label="Volver al índice del curso">← Curso</a>')
    document, count = re.subn(r"(<body\b[^>]*>)", r"\1\n" + link,
                              document, count=1, flags=re.I)
    if count != 1:
        raise ValueError("JupyterLite shell has no <body>")
    return document


def _copy_html_and_assets(output: Path, manifest: dict[str, object]) -> list[Path]:
    """Copy only the exact static allowlist; no repository discovery occurs here."""
    copied_html: list[Path] = []
    static_files = manifest["static_files"]
    assert isinstance(static_files, list)
    for relative in static_files:
        source = _source_file(relative)
        destination = output / relative
        if source.suffix.lower() == ".html":
            destination.parent.mkdir(parents=True, exist_ok=True)
            home = None if relative == Path("index.html") else _home_href(destination, output)
            document = augment_html(source.read_text(encoding="utf-8"), home)
            _assert_offline_html(document, relative.as_posix())
            destination.write_text(document, encoding="utf-8")
            copied_html.append(destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return copied_html


def _convert_notebooks(output: Path, manifest: dict[str, object]) -> list[Path]:
    exporter = HTMLExporter(template_name="lab")
    # The static view is a read-only fallback; executable Python lives in the
    # adjacent JupyterLite link. Never let nbconvert inject CDN dependencies.
    exporter.require_js_url = ""
    exporter.mathjax_url = ""
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    converted: list[Path] = []
    notebooks = manifest["notebooks"]
    assert isinstance(notebooks, list)
    for notebook_path in notebooks:
        source = _source_file(notebook_path)
        relative = notebook_path.with_suffix(".html")
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", MissingIDFieldWarning)
            notebook = nbformat.read(source, as_version=4)
            _assign_deterministic_cell_ids(notebook, notebook_path)
            _, notebook = normalize(notebook)
        rendered, resources = exporter.from_notebook_node(
            notebook, resources={"metadata": {"name": source.stem}}
        )
        document = augment_html(
            _strip_disabled_exporter_scripts(rendered),
            _home_href(destination, output),
            _lab_href(source, destination, output),
        )
        _assert_offline_html(document, relative.as_posix())
        destination.write_text(document, encoding="utf-8")
        for name, payload in resources.get("outputs", {}).items():
            asset = destination.parent / name
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_bytes(payload)
        converted.append(destination)
    return converted


def _notebook_sources(manifest: dict[str, object] | None = None) -> list[Path]:
    manifest = _load_public_manifest() if manifest is None else manifest
    notebooks = manifest["notebooks"]
    assert isinstance(notebooks, list)
    return [_source_file(relative) for relative in notebooks]


def _stage_lab_contents(contents: Path, manifest: dict[str, object]) -> tuple[int, int]:
    """Stage notebooks plus the local modules/data they need at runtime."""
    lab_files = manifest["lab_files"]
    notebooks = manifest["notebooks"]
    assert isinstance(lab_files, list) and isinstance(notebooks, list)
    converted_shell_cells = 0
    for relative in lab_files:
        source = _source_file(relative)
        destination = contents / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() != ".ipynb":
            shutil.copy2(source, destination)
            continue

        # JupyterLite has no OS subprocess. `%run file.py` preserves the
        # pedagogical intent while keeping repository notebooks untouched.
        notebook = json.loads(source.read_text(encoding="utf-8"))
        _assign_deterministic_cell_ids(notebook, relative)
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            original = cell.get("source", [])
            text = original if isinstance(original, str) else "".join(original)
            text, count = re.subn(r"(?m)^!python\s+([^\s]+\.py)\s*$", r"%run \1", text)
            if count:
                converted_shell_cells += count
                cell["source"] = text if isinstance(original, str) else text.splitlines(True)
        destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=1),
                               encoding="utf-8")
    return len(notebooks), converted_shell_cells


def _build_jupyterlite(output: Path, manifest: dict[str, object]) -> tuple[int, int]:
    """Build the editable browser lab as a Pages-only publication artifact."""
    with tempfile.TemporaryDirectory(prefix="algo-trading-jupyterlite-") as temporary:
        lite_dir = Path(temporary)
        contents = lite_dir / "files"
        notebook_count, converted_shell_cells = _stage_lab_contents(contents, manifest)
        config = {
            "jupyter-lite-schema-version": 0,
            "jupyter-config-data": {
                "appName": "Algo Trading · Laboratorio",
                "showLoadingIndicator": True,
                "litePluginSettings": {
                    "@jupyterlite/pyodide-kernel-extension:kernel": {
                        "disablePyPIFallback": True,
                        "pipliteUrls": [],
                    },
                },
            },
        }
        (lite_dir / "jupyter-lite.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        _pyodide_kernel_extension()
        pyodide_archive = _pyodide_archive()
        subprocess.run(
            [
                sys.executable, "-m", "jupyterlite_core.app", "build",
                "--lite-dir", str(lite_dir),
                "--output-dir", str(output / "jupyter"),
                "--apps", "lab",
                "--no-sourcemaps",
                "--no-unused-shared-packages",
                "--pyodide", str(pyodide_archive),
            ],
            cwd=lite_dir,
            check=True,
        )

    shell = output / "jupyter" / "lab" / "index.html"
    shell.write_text(
        augment_jupyterlite_shell(
            shell.read_text(encoding="utf-8"),
            os.path.relpath(output / "index.html", shell.parent).replace(os.sep, "/"),
        ),
        encoding="utf-8",
    )
    _canonicalize_jupyterlite_content_metadata(output / "jupyter")
    return notebook_count, converted_shell_cells


def _external_urls(value: object) -> list[str]:
    if isinstance(value, dict):
        return [url for item in value.values() for url in _external_urls(item)]
    if isinstance(value, list):
        return [url for item in value for url in _external_urls(item)]
    if isinstance(value, str) and urlsplit(value).scheme.lower() in {"http", "https"}:
        return [value]
    return []


def _local_hashed_url(root: Path, raw: object) -> Path:
    if not isinstance(raw, str):
        raise RuntimeError(f"offline package URL is not a string: {raw!r}")
    split = urlsplit(raw)
    hashes = parse_qs(split.query, keep_blank_values=True)
    if (split.scheme or split.netloc or split.fragment or not split.path.startswith("./")
            or set(hashes) != {"sha256"} or len(hashes["sha256"]) != 1
            or not re.fullmatch(r"[0-9a-f]{64}", hashes["sha256"][0])):
        raise RuntimeError(
            f"offline package URL is not same-origin and SHA-256 closed: {raw}"
        )
    target = (root / unquote(split.path)).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"offline package URL escapes JupyterLite: {raw}") from exc
    if target.is_symlink() or not target.is_file():
        raise RuntimeError(f"offline package URL target is missing or a symlink: {raw}")
    if _sha256(target) != hashes["sha256"][0]:
        raise RuntimeError(f"offline package URL SHA-256 mismatch: {raw}")
    return target


def _local_release_target(index: Path, jupyter: Path, raw: object) -> Path:
    if not isinstance(raw, str):
        raise RuntimeError(f"piplite release URL is not a string: {raw!r}")
    split = urlsplit(raw)
    if split.scheme or split.netloc or split.query or split.fragment or not split.path.startswith("./"):
        raise RuntimeError(f"piplite release URL is not same-origin relative: {raw}")
    target = (index.parent / unquote(split.path)).resolve()
    try:
        target.relative_to(jupyter.resolve())
    except ValueError as exc:
        raise RuntimeError(f"piplite release URL escapes JupyterLite: {raw}") from exc
    if target.is_symlink() or not target.is_file():
        raise RuntimeError(f"piplite release target is missing or a symlink: {raw}")
    return target


def _validate_piplite_index(index: Path, jupyter: Path) -> None:
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid piplite package index: {exc}") from exc
    if not isinstance(data, dict) or not data:
        raise RuntimeError("piplite package index is empty or malformed")
    release_count = 0
    for package, metadata in data.items():
        releases = metadata.get("releases") if isinstance(metadata, dict) else None
        if not isinstance(package, str) or not isinstance(releases, dict):
            raise RuntimeError("piplite package index contains malformed package metadata")
        for version, records in releases.items():
            if not isinstance(version, str) or not isinstance(records, list) or not records:
                raise RuntimeError(f"piplite package {package} has malformed releases")
            for record in records:
                if not isinstance(record, dict):
                    raise RuntimeError(f"piplite package {package} has a malformed release")
                expected = record.get("digests", {}).get("sha256")
                if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    raise RuntimeError(f"piplite package {package} has no SHA-256")
                target = _local_release_target(index, jupyter, record.get("url"))
                if _sha256(target) != expected:
                    raise RuntimeError(f"piplite package failed SHA-256 validation: {package}")
                release_count += 1
    if not release_count:
        raise RuntimeError("piplite package index contains no releases")


def _validate_core_files(pyodide_dir: Path, core_files: dict[str, str]) -> None:
    """Verify every file from the pinned core archive against its trusted hash."""
    for name, expected in core_files.items():
        target = pyodide_dir / name
        if (target.is_symlink() or not target.is_file()
                or _sha256(target) != expected):
            raise RuntimeError(f"Pyodide core file failed SHA-256 validation: {name}")


def _validate_offline_runtime(output: Path, manifest: dict[str, object]) -> None:
    """Require a same-origin, hash-closed Pyodide and piplite configuration."""
    validate_hardened_service_worker(output / "jupyter" / "service-worker.js")
    config_path = output / "jupyter" / "jupyter-lite.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JupyterLite configuration: {exc}") from exc
    kernel = (
        config.get("jupyter-config-data", {})
        .get("litePluginSettings", {})
        .get("@jupyterlite/pyodide-kernel-extension:kernel", {})
    )
    if kernel.get("pyodideUrl") != "./static/pyodide/pyodide.mjs":
        raise RuntimeError("JupyterLite Pyodide URL is not the pinned same-origin module")
    if kernel.get("disablePyPIFallback") is not True:
        raise RuntimeError("JupyterLite PyPI fallback must be disabled")
    piplite_urls = kernel.get("pipliteUrls")
    if not isinstance(piplite_urls, list) or not piplite_urls:
        raise RuntimeError("JupyterLite must declare at least one local piplite index")
    if _external_urls(config):
        raise RuntimeError("JupyterLite configuration contains an external URL")
    for raw in piplite_urls:
        index = _local_hashed_url(output / "jupyter", raw)
        _validate_piplite_index(index, output / "jupyter")

    pyodide_dir = output / "jupyter" / "static" / "pyodide"
    pyodide_identity = manifest["pyodide"]
    assert isinstance(pyodide_identity, dict)
    core_files = pyodide_identity["core_files"]
    assert isinstance(core_files, dict)
    _validate_core_files(pyodide_dir, core_files)
    try:
        lock = json.loads((pyodide_dir / "pyodide-lock.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid Pyodide lock: {exc}") from exc
    external = _external_urls(lock)
    if external:
        raise RuntimeError(f"Pyodide lock contains external URLs: {external[:3]}")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise RuntimeError("Pyodide lock contains no packages")
    declared_files: set[str] = set()
    for package, metadata in packages.items():
        declared_name = metadata.get("name") if isinstance(metadata, dict) else None
        if (not isinstance(declared_name, str)
                or re.sub(r"[-_.]+", "-", declared_name.lower())
                != re.sub(r"[-_.]+", "-", package.lower())):
            raise RuntimeError(f"Pyodide package metadata is malformed: {package}")
        filename = _manifest_relative(metadata.get("file_name"))
        if len(filename.parts) != 1 or filename.as_posix() in declared_files:
            raise RuntimeError(f"Pyodide package filename is unsafe or duplicated: {package}")
        declared_files.add(filename.as_posix())
        target = (pyodide_dir / filename).resolve()
        try:
            target.relative_to(pyodide_dir.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Pyodide package escapes runtime: {package}") from exc
        expected = metadata.get("sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise RuntimeError(f"Pyodide package has no valid SHA-256: {package}")
        # The official ``core`` archive intentionally ships the interpreter,
        # stdlib and lock, not all 359 optional wheels named by that lock.  An
        # absent wheel therefore stays unavailable offline.  If a wheel is
        # bundled, however, it must be a regular file with the locked digest.
        if target.exists() and (target.is_symlink() or not target.is_file()
                                or _sha256(target) != expected):
            raise RuntimeError(f"Pyodide package failed SHA-256 validation: {package}")


def _output_files(output: Path) -> list[Path]:
    """List regular output files while rejecting generated symlinks."""
    files: list[Path] = []
    for directory, dirnames, filenames in os.walk(output, followlinks=False):
        current = Path(directory)
        for dirname in dirnames:
            if (current / dirname).is_symlink():
                raise RuntimeError(f"generated output contains a directory symlink: {current / dirname}")
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink() or not stat.S_ISREG(candidate.stat().st_mode):
                raise RuntimeError(f"generated output contains a non-regular file: {candidate}")
            if candidate.name != OUTPUT_INTEGRITY_FILE:
                files.append(candidate)
    return sorted(files, key=lambda path: path.relative_to(output).as_posix())


def _harden_html_documents(output: Path) -> int:
    """Inject and verify the exact offline CSP in every generated HTML document."""
    documents = [path for path in _output_files(output) if path.suffix.lower() == ".html"]
    if not documents:
        raise RuntimeError("Pages build generated no HTML documents to harden")
    for path in documents:
        relative = path.relative_to(output).as_posix()
        document = path.read_text(encoding="utf-8")
        path.write_text(inject_offline_csp(document, relative), encoding="utf-8")
    return len(documents)


def _source_records(manifest: dict[str, object]) -> list[dict[str, object]]:
    """Hash the exact union of repository files declared for publication."""
    static_files = manifest["static_files"]
    lab_files = manifest["lab_files"]
    assert isinstance(static_files, list) and isinstance(lab_files, list)
    declared = {
        relative.as_posix(): relative
        for relative in [*static_files, *lab_files]
    }
    records: list[dict[str, object]] = []
    for identity, relative in sorted(declared.items()):
        source = _source_file(relative)
        records.append({
            "path": identity,
            "size": source.stat().st_size,
            "sha256": _sha256(source),
        })
    return records


def _build_input_records() -> list[dict[str, object]]:
    """Hash the exact policy, builder and dependency locks used for Pages."""
    records: list[dict[str, object]] = []
    for relative in BUILD_INPUT_PATHS:
        source = _source_file(relative)
        records.append({
            "path": relative.as_posix(),
            "size": source.stat().st_size,
            "sha256": _sha256(source),
        })
    return records


def _validated_github_sha(records: list[dict[str, object]]) -> str | None:
    """Bind CI provenance to HEAD and every declared provenance input."""
    github_sha = os.environ.get("GITHUB_SHA")
    if github_sha is None:
        return None
    if not GITHUB_SHA_RE.fullmatch(github_sha):
        raise RuntimeError("GITHUB_SHA must be exactly 40 lowercase hexadecimal characters")
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        raise RuntimeError("cannot verify GITHUB_SHA against repository HEAD") from exc
    if head != github_sha:
        raise RuntimeError("GITHUB_SHA does not match repository HEAD")
    for record in records:
        try:
            committed = subprocess.run(
                ["git", "show", f"{github_sha}:{record['path']}"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(
                f"cannot read Pages provenance input from GITHUB_SHA: {record['path']}"
            ) from exc
        if len(committed) != record["size"] or hashlib.sha256(committed).hexdigest() != record["sha256"]:
            raise RuntimeError(f"Pages provenance input differs from GITHUB_SHA: {record['path']}")
    return github_sha


def _write_integrity_manifest(
    output: Path, source_manifest: Path, manifest: dict[str, object]
) -> None:
    files = [
        {
            "path": path.relative_to(output).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in _output_files(output)
    ]
    pyodide_files = [
        item for item in files if item["path"].startswith("jupyter/static/pyodide/")
    ]
    config_path = output / "jupyter" / "jupyter-lite.json"
    build_inputs = _build_input_records()
    source_files = _source_records(manifest)
    integrity = {
        "schema": 2,
        "hash_algorithm": "SHA-256",
        "github_sha": _validated_github_sha([*build_inputs, *source_files]),
        "build_inputs": build_inputs,
        "source_manifest_sha256": _sha256(source_manifest),
        "source_files": source_files,
        "pyodide_archive_sha256": PYODIDE_ARCHIVE_SHA256,
        "config": {
            "path": config_path.relative_to(output).as_posix(),
            "sha256": _sha256(config_path),
        },
        "pyodide_files": pyodide_files,
        "files": files,
    }
    (output / OUTPUT_INTEGRITY_FILE).write_text(
        json.dumps(integrity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build(output: Path) -> tuple[int, int, int]:
    output = _safe_output(output)
    _validate_replacement_target(output)
    manifest = _load_public_manifest()
    # JupyterLite may retain shutdown-time references to its output path. Keep
    # that path in an isolated system-temp parent so a late toolchain cleanup
    # can never rematerialize an untracked staging tree inside the repository.
    # Promotion remains an atomic rename; fail closed if temp/workspace are on
    # different filesystems rather than silently degrading to a copy.
    with tempfile.TemporaryDirectory(prefix="algo-trading-pages-build-") as temporary:
        staging = Path(temporary) / output.name
        staging.mkdir(mode=0o700)
        if staging.stat().st_dev != output.parent.stat().st_dev:
            raise RuntimeError(
                "Pages staging and repository must share a filesystem for atomic promotion"
            )
        html_files = _copy_html_and_assets(staging, manifest)
        notebooks = _convert_notebooks(staging, manifest)
        lab_notebooks, converted_shell_cells = _build_jupyterlite(staging, manifest)
        if lab_notebooks != len(notebooks):
            raise RuntimeError(
                f"JupyterLite staged {lab_notebooks} notebooks; nbconvert rendered {len(notebooks)}"
            )
        harden_service_worker(staging / "jupyter" / "service-worker.js")
        _harden_html_documents(staging)
        (staging / ".nojekyll").touch()
        (staging / OUTPUT_OWNER_FILE).write_text(
            json.dumps(OUTPUT_OWNER, sort_keys=True) + "\n", encoding="utf-8"
        )
        _validate_offline_runtime(staging, manifest)
        _write_integrity_manifest(staging, PUBLIC_MANIFEST, manifest)
        _promote_output(staging, output)
        return len(html_files), len(notebooks), converted_shell_cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    html_count, notebook_count, converted_shell_cells = build(args.output)
    print(
        f"Pages site ready: {html_count} source HTML + {notebook_count} notebooks "
        f"+ JupyterLite ({converted_shell_cells} shell cells adapted)"
    )


if __name__ == "__main__":
    main()
