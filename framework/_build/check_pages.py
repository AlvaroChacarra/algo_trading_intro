"""Fail-closed acceptance checks for the generated GitHub Pages artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, unquote, urlsplit

_BUILD_HELPER_DIR = Path(__file__).resolve().parent
if str(_BUILD_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_BUILD_HELPER_DIR))
from pages_offline_policy import (  # noqa: E402
    inline_script_violations,
    offline_html_violations,
    validate_hardened_service_worker,
    validate_offline_html,
)


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_MANIFEST = Path(__file__).with_name("pages_public_manifest.json")
OWNER_FILE = ".pages-build-owned.json"
INTEGRITY_FILE = ".pages-integrity.json"
EXPECTED_OWNER = {"schema": 1, "owner": "algo-trading-build-pages"}
JUPYTERLITE_CANONICAL_TIMESTAMP = "1980-01-01T00:00:00.000000Z"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
GITHUB_SHA_RE = re.compile(r"[0-9a-f]{40}")
JUPYTERLITE_BOOTSTRAP_PACKAGES = frozenset({
    "comm", "ipykernel", "ipython", "jedi", "micropip", "piplite", "pyodide-kernel",
})
BUILD_INPUT_PATHS = (
    Path("framework/_build/build_pages.py"),
    Path("framework/_build/pages_offline_policy.py"),
    Path("framework/_build/pages_public_manifest.json"),
    Path("package-lock.json"),
    Path("requirements-pages-lock.txt"),
)
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


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.lab_hrefs: list[str] = []
        self.resource_urls: list[str] = []
        self.inline_scripts: list[str] = []
        self._script_chunks: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): value for name, value in attrs}
        normalized_tag = tag.lower()
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.urls.append(value)
        if normalized_tag == "object" and attributes.get("data"):
            self.urls.append(attributes["data"])
        if normalized_tag == "image" and attributes.get("xlink:href"):
            self.urls.append(attributes["xlink:href"])
        classes = set((attributes.get("class") or "").split())
        if normalized_tag == "a" and "course-lab" in classes and attributes.get("href"):
            self.lab_hrefs.append(attributes["href"])
        resource = None
        if normalized_tag in {
            "script", "img", "audio", "video", "source", "iframe", "embed",
        }:
            resource = attributes.get("src") or attributes.get("poster")
        elif normalized_tag == "object":
            resource = attributes.get("data")
        elif normalized_tag == "image":
            resource = attributes.get("href") or attributes.get("xlink:href")
        elif normalized_tag == "link" and set((attributes.get("rel") or "").lower().split()) & {
            "stylesheet", "icon", "preload", "modulepreload", "manifest",
        }:
            resource = attributes.get("href")
        if resource:
            self.resource_urls.append(resource)
        if normalized_tag == "script" and not attributes.get("src"):
            self._script_chunks = []

    def handle_data(self, data: str) -> None:
        if self._script_chunks is not None:
            self._script_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._script_chunks is not None:
            self.inline_scripts.append("".join(self._script_chunks))
            self._script_chunks = None


def _has_dynamic_external_call(inline_scripts: list[str]) -> bool:
    """Apply the shared inline-script policy used by the Pages builder."""
    return any(inline_script_violations(script) for script in inline_scripts)


def _external_runtime_urls(links: Links) -> list[str]:
    """Return browser-fetched resources that leave the Pages origin."""
    return [
        raw for raw in links.resource_urls
        if urlsplit(raw).scheme.lower() in {"http", "https"} or urlsplit(raw).netloc
    ]


def _has_external_runtime_resource(document: str, links: Links) -> bool:
    """Apply the same complete static-HTML decision as the Pages builder."""
    del links  # Kept in the signature for callers that also inspect navigation links.
    return bool(offline_html_violations(document))


def validate_lab_href(raw: str, expected_notebook: Path) -> None:
    split = urlsplit(raw)
    query = parse_qs(split.query, keep_blank_values=True)
    if (split.scheme or split.netloc or split.fragment
            or set(query) != {"path", "mode"}
            or query.get("path") != [expected_notebook.as_posix()]
            or query.get("mode") != ["single-document"]):
        raise ValueError(
            f"lab link does not identify {expected_notebook.as_posix()}: {raw}"
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> object:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"missing or symlinked {label}: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid {label}: {exc}") from exc


def _validate_projection_destinations(
    static_files: list[Path], lab_files: list[Path], notebooks: list[Path]
) -> None:
    reserved = {".nojekyll", OWNER_FILE, INTEGRITY_FILE}
    static_outputs = [item.as_posix() for item in static_files]
    notebook_outputs = [item.with_suffix(".html").as_posix() for item in notebooks]
    public_outputs = static_outputs + notebook_outputs
    if (any(path in reserved or path.startswith("jupyter/") for path in static_outputs)
            or len({path.casefold() for path in public_outputs}) != len(public_outputs)
            or len({item.as_posix().casefold() for item in lab_files}) != len(lab_files)):
        raise RuntimeError("Pages public manifest contains reserved or colliding destinations")


def _manifest_relative(raw: object) -> Path:
    if not isinstance(raw, str) or not raw:
        raise RuntimeError(f"invalid manifest path: {raw!r}")
    if "\\" in raw or ":" in raw or any(ord(character) < 32 for character in raw):
        raise RuntimeError(f"non-canonical manifest path: {raw!r}")
    pure = PurePosixPath(raw)
    if (pure.is_absolute() or pure.as_posix() != raw
            or any(part in {"", ".", ".."} for part in pure.parts)):
        raise RuntimeError(f"non-canonical manifest path: {raw!r}")
    return Path(*pure.parts)


def _load_source_manifest(path: Path = PUBLIC_MANIFEST) -> dict[str, object]:
    data = _read_json(path, "Pages public manifest")
    if not isinstance(data, dict) or set(data) != {
        "schema", "pyodide", "static_files", "lab_files",
    }:
        raise RuntimeError("Pages public manifest has unexpected or missing fields")
    if data["schema"] != 1:
        raise RuntimeError("unsupported Pages public manifest schema")
    pyodide = data["pyodide"]
    if (not isinstance(pyodide, dict)
            or set(pyodide) != {"version", "archive", "archive_sha256", "core_files"}
            or not isinstance(pyodide["version"], str)
            or pyodide["archive"] != f"pyodide-core-{pyodide['version']}.tar.bz2"
            or not isinstance(pyodide["archive_sha256"], str)
            or not SHA256_RE.fullmatch(pyodide["archive_sha256"])):
        raise RuntimeError("Pages public manifest has an invalid Pyodide identity")
    core_files = pyodide["core_files"]
    if (not isinstance(core_files, dict)
            or set(core_files) != PYODIDE_CORE_FILE_NAMES
            or list(core_files) != sorted(core_files)
            or any(not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
                   for digest in core_files.values())):
        raise RuntimeError("Pages public manifest has an invalid Pyodide core hash map")

    parsed: dict[str, object] = {"schema": 1, "pyodide": pyodide}
    for field in ("static_files", "lab_files"):
        values = data[field]
        if not isinstance(values, list):
            raise RuntimeError(f"Pages public manifest {field} must be a list")
        paths = [_manifest_relative(value) for value in values]
        identities = [item.as_posix() for item in paths]
        if identities != sorted(identities) or len(identities) != len(set(identities)):
            raise RuntimeError(f"Pages public manifest {field} must be sorted and unique")
        parsed[field] = paths

    static_files = parsed["static_files"]
    lab_files = parsed["lab_files"]
    assert isinstance(static_files, list) and isinstance(lab_files, list)
    # The same declared source may be required by both projections (for
    # example a CSV rendered on the static site and staged in JupyterLite).
    notebooks = [item for item in lab_files if item.suffix.lower() == ".ipynb"]
    if len(notebooks) != 28:
        raise RuntimeError(
            f"Pages public manifest must contain exactly 28 core notebooks, found {len(notebooks)}"
        )
    parsed["notebooks"] = notebooks
    _validate_projection_destinations(static_files, lab_files, notebooks)
    return parsed


def _regular_files(root: Path, *, exclude: set[str] | None = None) -> dict[str, Path]:
    """Return every regular file below root and reject every symlink/special file."""
    excluded = set() if exclude is None else exclude
    files: dict[str, Path] = {}
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(directory)
        for dirname in dirnames:
            candidate = current / dirname
            if candidate.is_symlink():
                raise RuntimeError(f"artifact contains a directory symlink: {candidate}")
        for filename in filenames:
            candidate = current / filename
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_symlink() or not stat.S_ISREG(candidate.stat().st_mode):
                raise RuntimeError(f"artifact contains a non-regular file: {relative}")
            if relative not in excluded:
                files[relative] = candidate
    return files


def _safe_site_target(site: Path, relative: Path) -> Path:
    target = (site / relative).resolve(strict=False)
    try:
        target.relative_to(site.resolve())
    except ValueError as exc:
        raise RuntimeError(f"artifact path escapes the site: {relative.as_posix()}") from exc
    return target


def local_target(page: Path, raw: str, site: Path, base_path: str) -> Path | None:
    """Resolve an HTML URL while proving it remains inside the checked site."""
    split = urlsplit(raw)
    if split.scheme or split.netloc or raw.startswith(("#", "data:", "mailto:")):
        return None
    decoded = unquote(split.path)
    if "\\" in raw or "\\" in decoded or "%5c" in raw.lower():
        raise ValueError(f"local URL contains a forbidden backslash: {raw}")
    if not decoded:
        return None
    if decoded.startswith("/"):
        if not decoded.startswith(base_path):
            raise ValueError(f"root-relative URL escapes Pages base path: {raw}")
        unresolved = site / decoded[len(base_path):]
    else:
        unresolved = page.parent / decoded
    target = unresolved.resolve(strict=False)
    try:
        target.relative_to(site.resolve())
    except ValueError as exc:
        raise ValueError(f"local URL escapes the Pages artifact: {raw}") from exc
    return target


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
        raise RuntimeError(f"offline URL is not a string: {raw!r}")
    split = urlsplit(raw)
    query = parse_qs(split.query, keep_blank_values=True)
    if (split.scheme or split.netloc or split.fragment or not split.path.startswith("./")
            or set(query) != {"sha256"} or len(query["sha256"]) != 1
            or not SHA256_RE.fullmatch(query["sha256"][0])):
        raise RuntimeError(f"offline URL is not same-origin and SHA-256 closed: {raw}")
    target = (root / unquote(split.path)).resolve(strict=False)
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"offline URL escapes JupyterLite: {raw}") from exc
    if target.is_symlink() or not target.is_file():
        raise RuntimeError(f"offline URL target is missing or symlinked: {raw}")
    if _sha256(target) != query["sha256"][0]:
        raise RuntimeError(f"offline URL SHA-256 mismatch: {raw}")
    return target


def _local_release_target(index: Path, jupyter: Path, raw: object) -> Path:
    if not isinstance(raw, str):
        raise RuntimeError(f"piplite release URL is not a string: {raw!r}")
    split = urlsplit(raw)
    if split.scheme or split.netloc or split.query or split.fragment or not split.path.startswith("./"):
        raise RuntimeError(f"piplite release URL is not same-origin relative: {raw}")
    target = (index.parent / unquote(split.path)).resolve(strict=False)
    try:
        target.relative_to(jupyter.resolve())
    except ValueError as exc:
        raise RuntimeError(f"piplite release URL escapes JupyterLite: {raw}") from exc
    if target.is_symlink() or not target.is_file():
        raise RuntimeError(f"piplite release target is missing or symlinked: {raw}")
    return target


def _canonical_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.lower())


def _validate_piplite_index(index: Path, jupyter: Path) -> set[str]:
    data = _read_json(index, "piplite package index")
    if not isinstance(data, dict) or not data:
        raise RuntimeError("piplite package index is empty or malformed")
    release_count = 0
    package_names: set[str] = set()
    for package, metadata in data.items():
        releases = metadata.get("releases") if isinstance(metadata, dict) else None
        if not isinstance(package, str) or not isinstance(releases, dict):
            raise RuntimeError("piplite package index contains malformed package metadata")
        package_names.add(_canonical_package_name(package))
        for version, records in releases.items():
            if not isinstance(version, str) or not isinstance(records, list) or not records:
                raise RuntimeError(f"piplite package {package} has malformed releases")
            for record in records:
                if not isinstance(record, dict):
                    raise RuntimeError(f"piplite package {package} has a malformed release")
                digest = record.get("digests", {}).get("sha256")
                if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                    raise RuntimeError(f"piplite package {package} has no SHA-256")
                target = _local_release_target(index, jupyter, record.get("url"))
                if _sha256(target) != digest:
                    raise RuntimeError(f"piplite package {package} failed its SHA-256 check")
                release_count += 1
    if not release_count:
        raise RuntimeError("piplite package index contains no releases")
    return package_names


def _validate_kernel_bootstrap_packages(
    piplite_packages: set[str], pyodide_packages: set[str],
) -> None:
    available = {
        _canonical_package_name(name) for name in piplite_packages | pyodide_packages
    }
    missing = sorted(JUPYTERLITE_BOOTSTRAP_PACKAGES - available)
    if missing:
        raise RuntimeError(
            f"JupyterLite offline kernel bootstrap packages are missing: {missing}"
        )


def _validate_core_files(pyodide_dir: Path, core_files: dict[str, str]) -> None:
    """Verify every file from the pinned core archive against its trusted hash."""
    for name, expected in core_files.items():
        target = pyodide_dir / name
        if (target.is_symlink() or not target.is_file()
                or _sha256(target) != expected):
            raise RuntimeError(f"Pyodide core file failed SHA-256 validation: {name}")


def _validate_jupyterlite_content_metadata(jupyter: Path) -> None:
    api_files = sorted((jupyter / "api" / "contents").glob("**/all.json"))
    if not api_files:
        raise RuntimeError("JupyterLite has no static contents metadata")

    def visit(value: object, path: Path) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if (key in {"created", "last_modified"}
                        and item != JUPYTERLITE_CANONICAL_TIMESTAMP):
                    raise RuntimeError(
                        f"JupyterLite contents metadata is not deterministic: {path}"
                    )
                visit(item, path)
        elif isinstance(value, list):
            for item in value:
                visit(item, path)

    for path in api_files:
        visit(_read_json(path, "JupyterLite contents metadata"), path)


def _validate_offline_runtime(site: Path, manifest: dict[str, object]) -> None:
    jupyter = site / "jupyter"
    validate_hardened_service_worker(jupyter / "service-worker.js")
    _validate_jupyterlite_content_metadata(jupyter)
    config_path = jupyter / "jupyter-lite.json"
    config = _read_json(config_path, "JupyterLite configuration")
    if not isinstance(config, dict):
        raise RuntimeError("JupyterLite configuration is not an object")
    external = _external_urls(config)
    if external:
        raise RuntimeError(f"JupyterLite configuration contains external URLs: {external[:3]}")
    kernel = (
        config.get("jupyter-config-data", {})
        .get("litePluginSettings", {})
        .get("@jupyterlite/pyodide-kernel-extension:kernel", {})
    )
    if not isinstance(kernel, dict):
        raise RuntimeError("JupyterLite Pyodide kernel configuration is malformed")
    if kernel.get("pyodideUrl") != "./static/pyodide/pyodide.mjs":
        raise RuntimeError("JupyterLite Pyodide runtime is not the pinned same-origin module")
    if kernel.get("disablePyPIFallback") is not True:
        raise RuntimeError("JupyterLite PyPI fallback is not disabled")
    piplite_urls = kernel.get("pipliteUrls")
    if not isinstance(piplite_urls, list) or not piplite_urls:
        raise RuntimeError("JupyterLite has no local SHA-256-pinned piplite index")
    piplite_packages: set[str] = set()
    for raw in piplite_urls:
        piplite_packages.update(
            _validate_piplite_index(_local_hashed_url(jupyter, raw), jupyter)
        )

    pyodide = jupyter / "static" / "pyodide"
    pyodide_identity = manifest["pyodide"]
    assert isinstance(pyodide_identity, dict)
    core_files = pyodide_identity["core_files"]
    assert isinstance(core_files, dict)
    _validate_core_files(pyodide, core_files)
    lock = _read_json(pyodide / "pyodide-lock.json", "Pyodide lock")
    if not isinstance(lock, dict) or _external_urls(lock):
        raise RuntimeError("Pyodide lock is malformed or contains external URLs")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise RuntimeError("Pyodide lock contains no packages")
    _validate_kernel_bootstrap_packages(piplite_packages, set(packages))
    declared_files: set[str] = set()
    for package, metadata in packages.items():
        declared_name = metadata.get("name") if isinstance(metadata, dict) else None
        if (not isinstance(declared_name, str)
                or re.sub(r"[-_.]+", "-", declared_name.lower())
                != re.sub(r"[-_.]+", "-", package.lower())):
            raise RuntimeError(f"Pyodide package metadata is malformed: {package}")
        relative = _manifest_relative(metadata.get("file_name"))
        if len(relative.parts) != 1 or relative.as_posix() in declared_files:
            raise RuntimeError(f"Pyodide package filename is unsafe or duplicated: {package}")
        declared_files.add(relative.as_posix())
        target = _safe_site_target(pyodide, relative)
        digest = metadata.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise RuntimeError(f"Pyodide package has no valid SHA-256: {package}")
        # ``pyodide-core`` does not contain every optional wheel in its lock.
        # Missing wheels cannot be fetched externally (the configuration is
        # same-origin and fallback is disabled); any bundled wheel must match.
        if target.exists() and (target.is_symlink() or not target.is_file()
                                or _sha256(target) != digest):
            raise RuntimeError(f"Pyodide package failed SHA-256 validation: {package}")


def _verify_source_records(
    records: object, manifest: dict[str, object], github_sha: object = None
) -> None:
    """Recompute the declared repository-source hashes from the current checkout."""
    if not isinstance(records, list) or not records:
        raise RuntimeError("Pages integrity manifest contains no source files")
    parsed: dict[str, tuple[Path, dict[str, object]]] = {}
    identities: list[str] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"path", "size", "sha256"}:
            raise RuntimeError("Pages integrity manifest contains a malformed source record")
        relative = _manifest_relative(record["path"])
        identity = relative.as_posix()
        if (not isinstance(record["size"], int) or isinstance(record["size"], bool)
                or record["size"] < 0 or not isinstance(record["sha256"], str)
                or not SHA256_RE.fullmatch(record["sha256"]) or identity in parsed):
            raise RuntimeError(f"Pages source integrity record is malformed: {identity}")
        identities.append(identity)
        parsed[identity] = (relative, record)
    if identities != sorted(identities):
        raise RuntimeError("Pages source integrity records must be sorted")

    static_files = manifest["static_files"]
    lab_files = manifest["lab_files"]
    assert isinstance(static_files, list) and isinstance(lab_files, list)
    expected = {item.as_posix() for item in [*static_files, *lab_files]}
    if set(parsed) != expected:
        missing = sorted(expected - set(parsed))[:5]
        extra = sorted(set(parsed) - expected)[:5]
        raise RuntimeError(f"Pages source file set differs: missing={missing}, extra={extra}")
    for identity, (relative, record) in parsed.items():
        source = _repository_file(relative)
        if (not source.is_file() or source.stat().st_size != record["size"]
                or _sha256(source) != record["sha256"]):
            raise RuntimeError(f"Pages declared source failed integrity validation: {identity}")
    committed_sha = _validated_artifact_sha(github_sha)
    if committed_sha is not None:
        _verify_committed_records(
            {identity: record for identity, (_relative, record) in parsed.items()},
            committed_sha,
            "source",
        )


def _repository_file(relative: Path) -> Path:
    """Resolve a provenance input without following repository symlinks."""
    candidate = ROOT
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise RuntimeError(
                f"Pages provenance input must not be a symlink: {relative.as_posix()}"
            )
    if not candidate.is_file():
        raise RuntimeError(f"Pages provenance input is missing: {relative.as_posix()}")
    return candidate


def _validated_artifact_sha(github_sha: object) -> str | None:
    """Validate optional artifact provenance against the environment and HEAD."""
    environment_sha = os.environ.get("GITHUB_SHA")
    if environment_sha is not None and not GITHUB_SHA_RE.fullmatch(environment_sha):
        raise RuntimeError("GITHUB_SHA must be exactly 40 lowercase hexadecimal characters")
    if github_sha is None:
        if environment_sha is not None:
            raise RuntimeError("Pages artifact is missing GITHUB_SHA provenance")
        return None
    if not isinstance(github_sha, str) or not GITHUB_SHA_RE.fullmatch(github_sha):
        raise RuntimeError("Pages artifact contains an invalid GITHUB_SHA")
    if environment_sha is not None and github_sha != environment_sha:
        raise RuntimeError("Pages artifact GITHUB_SHA differs from the CI environment")
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        raise RuntimeError("cannot verify Pages artifact GITHUB_SHA against HEAD") from exc
    if head != github_sha:
        raise RuntimeError("Pages artifact GITHUB_SHA does not match repository HEAD")
    return github_sha


def _verify_committed_records(
    records: dict[str, dict[str, object]], github_sha: str, label: str
) -> None:
    """Bind validated checkout records to the bytes stored in a commit."""
    for identity, record in records.items():
        try:
            committed = subprocess.run(
                ["git", "show", f"{github_sha}:{identity}"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(
                f"cannot read Pages {label} from GITHUB_SHA: {identity}"
            ) from exc
        if (len(committed) != record["size"]
                or hashlib.sha256(committed).hexdigest() != record["sha256"]):
            raise RuntimeError(
                f"Pages {label} differs from artifact GITHUB_SHA: {identity}"
            )


def _verify_build_inputs(records: object, github_sha: object) -> dict[str, dict[str, object]]:
    """Verify build policy/tool locks and bind CI records to committed HEAD bytes."""
    environment_sha = os.environ.get("GITHUB_SHA")
    if environment_sha is not None and not GITHUB_SHA_RE.fullmatch(environment_sha):
        raise RuntimeError("GITHUB_SHA must be exactly 40 lowercase hexadecimal characters")
    if not isinstance(records, list):
        raise RuntimeError("Pages integrity manifest has malformed build inputs")
    parsed: dict[str, dict[str, object]] = {}
    identities: list[str] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"path", "size", "sha256"}:
            raise RuntimeError("Pages integrity manifest contains a malformed build input")
        relative = _manifest_relative(record["path"])
        identity = relative.as_posix()
        if (not isinstance(record["size"], int) or isinstance(record["size"], bool)
                or record["size"] < 0 or not isinstance(record["sha256"], str)
                or not SHA256_RE.fullmatch(record["sha256"]) or identity in parsed):
            raise RuntimeError(f"Pages build input record is malformed: {identity}")
        identities.append(identity)
        parsed[identity] = record
    expected = [path.as_posix() for path in BUILD_INPUT_PATHS]
    if identities != expected:
        raise RuntimeError(
            f"Pages build input set differs: expected={expected}, actual={identities}"
        )
    for identity, record in parsed.items():
        target = _repository_file(Path(identity))
        if target.stat().st_size != record["size"] or _sha256(target) != record["sha256"]:
            raise RuntimeError(f"Pages build input failed integrity validation: {identity}")

    committed_sha = _validated_artifact_sha(github_sha)
    if committed_sha is not None:
        _verify_committed_records(parsed, committed_sha, "build input")
    return parsed


def _verify_integrity(site: Path, manifest: dict[str, object]) -> dict[str, Path]:
    owner = _read_json(site / OWNER_FILE, "Pages ownership marker")
    if owner != EXPECTED_OWNER:
        raise RuntimeError("Pages ownership marker has the wrong identity")
    integrity = _read_json(site / INTEGRITY_FILE, "Pages integrity manifest")
    expected_fields = {
        "schema", "hash_algorithm", "github_sha", "build_inputs", "source_manifest_sha256",
        "source_files", "pyodide_archive_sha256", "config", "pyodide_files", "files",
    }
    if not isinstance(integrity, dict) or set(integrity) != expected_fields:
        raise RuntimeError("Pages integrity manifest has unexpected or missing fields")
    if integrity["schema"] != 2 or integrity["hash_algorithm"] != "SHA-256":
        raise RuntimeError("Pages integrity manifest has an unsupported schema or hash")
    build_inputs = _verify_build_inputs(integrity["build_inputs"], integrity["github_sha"])
    if integrity["source_manifest_sha256"] != _sha256(PUBLIC_MANIFEST):
        raise RuntimeError("Pages artifact was not built from the checked public manifest")
    manifest_identity = "framework/_build/pages_public_manifest.json"
    if build_inputs[manifest_identity]["sha256"] != integrity["source_manifest_sha256"]:
        raise RuntimeError("Pages public manifest provenance is internally inconsistent")
    _verify_source_records(integrity["source_files"], manifest, integrity["github_sha"])
    pyodide = manifest["pyodide"]
    assert isinstance(pyodide, dict)
    if integrity["pyodide_archive_sha256"] != pyodide["archive_sha256"]:
        raise RuntimeError("Pages artifact records the wrong Pyodide archive SHA-256")

    records = integrity["files"]
    if not isinstance(records, list) or not records:
        raise RuntimeError("Pages integrity manifest contains no files")
    parsed: dict[str, dict[str, object]] = {}
    identities: list[str] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"path", "size", "sha256"}:
            raise RuntimeError("Pages integrity manifest contains a malformed file record")
        relative = _manifest_relative(record["path"])
        identity = relative.as_posix()
        if (not isinstance(record["size"], int) or isinstance(record["size"], bool)
                or record["size"] < 0 or not isinstance(record["sha256"], str)
                or not SHA256_RE.fullmatch(record["sha256"])):
            raise RuntimeError(f"Pages integrity record is malformed: {identity}")
        if identity in parsed:
            raise RuntimeError(f"Pages integrity manifest duplicates a file: {identity}")
        identities.append(identity)
        parsed[identity] = record
    if identities != sorted(identities):
        raise RuntimeError("Pages integrity file set must be sorted")

    actual = _regular_files(site, exclude={INTEGRITY_FILE})
    if set(actual) != set(parsed):
        missing = sorted(set(parsed) - set(actual))[:5]
        extra = sorted(set(actual) - set(parsed))[:5]
        raise RuntimeError(f"Pages public file set differs: missing={missing}, extra={extra}")
    for identity, target in actual.items():
        record = parsed[identity]
        if target.stat().st_size != record["size"] or _sha256(target) != record["sha256"]:
            raise RuntimeError(f"Pages public file failed integrity validation: {identity}")

    config = integrity["config"]
    if (not isinstance(config, dict) or set(config) != {"path", "sha256"}
            or config.get("path") != "jupyter/jupyter-lite.json"
            or config.get("sha256") != parsed.get("jupyter/jupyter-lite.json", {}).get("sha256")):
        raise RuntimeError("Pages integrity manifest does not pin the JupyterLite configuration")
    expected_pyodide = [
        record for record in records
        if record["path"].startswith("jupyter/static/pyodide/")
    ]
    if integrity["pyodide_files"] != expected_pyodide or not expected_pyodide:
        raise RuntimeError("Pages integrity manifest does not pin the exact Pyodide file set")
    core_files = pyodide["core_files"]
    assert isinstance(core_files, dict)
    core_prefix = "jupyter/static/pyodide/"
    recorded_core = {
        record["path"][len(core_prefix):]: record["sha256"]
        for record in expected_pyodide
        if record["path"][len(core_prefix):] in core_files
    }
    if recorded_core != core_files:
        raise RuntimeError("Pages integrity manifest does not match the pinned Pyodide core")

    static_files = manifest["static_files"]
    lab_files = manifest["lab_files"]
    notebooks = manifest["notebooks"]
    assert isinstance(static_files, list) and isinstance(lab_files, list)
    assert isinstance(notebooks, list)
    expected_public = {
        *(item.as_posix() for item in static_files),
        *(item.with_suffix(".html").as_posix() for item in notebooks),
        ".nojekyll",
        OWNER_FILE,
    }
    actual_public = {identity for identity in actual if not identity.startswith("jupyter/")}
    if actual_public != expected_public:
        missing = sorted(expected_public - actual_public)[:5]
        extra = sorted(actual_public - expected_public)[:5]
        raise RuntimeError(f"closed-world public projection differs: missing={missing}, extra={extra}")
    expected_contents = {item.as_posix() for item in lab_files}
    actual_contents = {
        identity[len("jupyter/files/"):]
        for identity in actual if identity.startswith("jupyter/files/")
    }
    if actual_contents != expected_contents:
        missing = sorted(expected_contents - actual_contents)[:5]
        extra = sorted(actual_contents - expected_contents)[:5]
        raise RuntimeError(f"closed-world Jupyter inputs differ: missing={missing}, extra={extra}")
    return actual


def check_site(site_arg: Path, base_path: str) -> tuple[list[str], int, int]:
    failures: list[str] = []
    if not re.fullmatch(r"/(?:[^/]+/)*", base_path):
        return [f"base path must be an absolute directory path: {base_path}"], 0, 0
    if site_arg.is_symlink() or not site_arg.is_dir():
        return [f"site root is missing, not a directory, or a symlink: {site_arg}"], 0, 0
    site = site_arg.resolve()
    try:
        manifest = _load_source_manifest()
        actual = _verify_integrity(site, manifest)
        _validate_offline_runtime(site, manifest)
    except (OSError, RuntimeError, ValueError) as exc:
        return [str(exc)], 0, 0

    html_files = sorted(
        (target for identity, target in actual.items() if identity.endswith(".html")),
        key=lambda item: item.relative_to(site).as_posix(),
    )
    notebooks = manifest["notebooks"]
    assert isinstance(notebooks, list)
    lab_notebooks = [site / "jupyter" / "files" / item for item in notebooks]

    lab_shell = site / "jupyter" / "lab" / "index.html"
    if not lab_shell.is_file():
        failures.append("missing JupyterLite lab shell")
    else:
        shell_text = lab_shell.read_text(encoding="utf-8")
        if "course-home" not in shell_text:
            failures.append("JupyterLite lab has no course return link")
        if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', shell_text, re.I):
            failures.append("JupyterLite lab is missing viewport")

    for notebook, relative in zip(lab_notebooks, notebooks, strict=True):
        rendered = site / relative.with_suffix(".html")
        if not rendered.is_file():
            failures.append(f"JupyterLite notebook has no rendered HTML pair: {relative}")
        try:
            notebook_data = _read_json(notebook, f"published notebook {relative}")
        except RuntimeError as exc:
            failures.append(str(exc))
            continue
        cells = notebook_data.get("cells", []) if isinstance(notebook_data, dict) else []
        source = "\n".join(
            cell.get("source", "") if isinstance(cell.get("source", ""), str)
            else "".join(cell.get("source", []))
            for cell in cells if isinstance(cell, dict) and cell.get("cell_type") == "code"
        )
        if re.search(r"(?m)^!python\s+", source):
            failures.append(f"unsupported shell cell remains in JupyterLite: {relative}")

    index_path = site / "index.html"
    if not index_path.is_file():
        failures.append("missing index.html")
        index = ""
    else:
        index = index_path.read_text(encoding="utf-8")
    for number in range(1, 15):
        for suffix in (f"{number:02d}_build_exercises.html", f"{number:02d}_auxiliary.html"):
            matches = [
                target for target in html_files
                if target.name == suffix and target.parent.name == "exercises"
            ]
            if len(matches) != 1:
                failures.append(f"expected one rendered notebook: {suffix}")
            elif suffix not in index:
                failures.append(f"index does not link {suffix}")
    if len(re.findall(r'class="lc-actions"', index)) != 14:
        failures.append("index must expose three actions for each of the 14 classes")

    for page in html_files:
        relative = page.relative_to(site)
        text = page.read_text(encoding="utf-8")
        try:
            validate_offline_html(text, relative.as_posix(), require_csp=True)
        except RuntimeError as exc:
            failures.append(str(exc))
        if relative.parts[0] == "jupyter":
            continue
        if not re.search(r'<meta\s+[^>]*name=["\']viewport["\']', text, re.I):
            failures.append(f"missing viewport: {relative}")
        if relative != Path("index.html") and "course-home" not in text:
            failures.append(f"missing course return link: {relative}")
        if relative.with_suffix(".ipynb") in notebooks and "course-lab" not in text:
            failures.append(f"rendered notebook has no editable lab link: {relative}")
        parser_links = Links()
        parser_links.feed(text)
        expected_notebook = relative.with_suffix(".ipynb")
        if expected_notebook in notebooks:
            if len(parser_links.lab_hrefs) != 1:
                failures.append(f"rendered notebook has {len(parser_links.lab_hrefs)} lab links: {relative}")
            else:
                try:
                    validate_lab_href(parser_links.lab_hrefs[0], expected_notebook)
                except ValueError as exc:
                    failures.append(f"{relative}: {exc}")
        for raw in parser_links.urls:
            try:
                target = local_target(page, raw, site, base_path)
            except ValueError as exc:
                failures.append(f"{relative}: {exc}")
                continue
            if target is not None and not target.exists():
                failures.append(f"broken link in {relative}: {raw}")
    return failures, len(html_files), len(lab_notebooks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", type=Path)
    parser.add_argument("--base-path", default="/algo_trading_intro/")
    args = parser.parse_args()
    failures, html_count, notebook_count = check_site(args.site, args.base_path)
    if failures:
        print("Pages checks failed:")
        for failure in failures[:100]:
            print(f"- {failure}")
        sys.exit(1)
    print(
        f"Pages checks passed: {html_count} HTML files, "
        f"{notebook_count} editable notebooks, base {args.base_path}"
    )


if __name__ == "__main__":
    main()
