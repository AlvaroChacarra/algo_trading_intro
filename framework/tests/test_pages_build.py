from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

import nbformat
import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "course_build_pages", ROOT / "framework/_build/build_pages.py"
)
assert SPEC and SPEC.loader
BUILD_PAGES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_PAGES)
CHECK_SPEC = importlib.util.spec_from_file_location(
    "course_check_pages", ROOT / "framework/_build/check_pages.py"
)
assert CHECK_SPEC and CHECK_SPEC.loader
CHECK_PAGES = importlib.util.module_from_spec(CHECK_SPEC)
CHECK_SPEC.loader.exec_module(CHECK_PAGES)
import pages_offline_policy as OFFLINE_POLICY


def _extension(root: Path, package_version: str) -> Path:
    extension = root / "@jupyterlite" / "pyodide-kernel-extension"
    extension.mkdir(parents=True)
    (extension / "package.json").write_text(
        json.dumps({
            "name": "@jupyterlite/pyodide-kernel-extension",
            "version": package_version,
        }),
        encoding="utf-8",
    )
    return extension


def test_pyodide_extension_resolver_requires_the_pinned_matching_frontend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    exact_root = tmp_path / "share/jupyter/labextensions"
    exact = _extension(exact_root, "0.8.1")
    monkeypatch.setattr(BUILD_PAGES, "version", lambda _name: "0.8.1")
    monkeypatch.setattr(BUILD_PAGES.sys, "prefix", str(tmp_path))
    assert BUILD_PAGES._pyodide_kernel_extension() == exact.resolve()


def test_pyodide_extension_resolver_fails_closed_when_frontend_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(BUILD_PAGES, "version", lambda _name: "0.8.1")
    monkeypatch.setattr(BUILD_PAGES.sys, "prefix", str(tmp_path))
    with pytest.raises(RuntimeError, match="0.8.1 was not found"):
        BUILD_PAGES._pyodide_kernel_extension()


def test_jupyterlite_build_relies_on_single_autodiscovered_kernel_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    extension = tmp_path / "labextensions/@jupyterlite/pyodide-kernel-extension"
    archive = tmp_path / "pyodide.tar.bz2"
    archive.write_bytes(b"pinned-pyodide")
    comm_wheel = tmp_path / "comm.whl"
    comm_wheel.write_bytes(b"pinned-comm")
    calls: list[list[str]] = []
    extension_checks = 0

    def resolve_extension() -> Path:
        nonlocal extension_checks
        extension_checks += 1
        return extension

    def fake_run(command: list[str], **_kwargs: object) -> None:
        calls.append(command)
        output = Path(command[command.index("--output-dir") + 1])
        (output / "lab").mkdir(parents=True)
        (output / "lab/index.html").write_text(
            "<!doctype html><html><head></head><body></body></html>",
            encoding="utf-8",
        )
        metadata = output / "api/contents/all.json"
        metadata.parent.mkdir(parents=True)
        metadata.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(BUILD_PAGES, "_pyodide_kernel_extension", resolve_extension)
    monkeypatch.setattr(BUILD_PAGES, "_pyodide_archive", lambda: archive)
    monkeypatch.setattr(BUILD_PAGES, "_comm_wheel", lambda: comm_wheel)
    monkeypatch.setattr(BUILD_PAGES.subprocess, "run", fake_run)

    output = tmp_path / "site"
    output.mkdir()
    assert BUILD_PAGES._build_jupyterlite(
        output, {"lab_files": [], "notebooks": []}
    ) == (0, 0)

    assert extension_checks == 1
    assert len(calls) == 1
    command = calls[0]
    assert not any("federated_extensions" in argument for argument in command)
    assert command[command.index("--source-date-epoch") + 1] == str(
        BUILD_PAGES.JUPYTERLITE_SOURCE_DATE_EPOCH
    )
    assert command[command.index("--pyodide") + 1] == str(archive)
    assert command[command.index("--piplite-wheels") + 1] == str(comm_wheel)


def test_pyodide_archive_accepts_only_the_pinned_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    archive = tmp_path / "pyodide.tar.bz2"
    archive.write_bytes(b"exact-pyodide-fixture")
    monkeypatch.setenv("WORK2_PYODIDE_ARCHIVE", str(archive))
    monkeypatch.setattr(
        BUILD_PAGES, "PYODIDE_ARCHIVE_SHA256", BUILD_PAGES._sha256(archive)
    )
    assert BUILD_PAGES._pyodide_archive() == archive.resolve()

    archive.write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="SHA-256"):
        BUILD_PAGES._pyodide_archive()


def test_pyodide_archive_requires_a_real_supplied_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "missing.tar.bz2"
    monkeypatch.setenv("WORK2_PYODIDE_ARCHIVE", str(missing))
    with pytest.raises(RuntimeError, match="does not exist"):
        BUILD_PAGES._pyodide_archive()


def test_comm_wheel_accepts_only_the_pinned_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheel = tmp_path / "comm.whl"
    wheel.write_bytes(b"exact-comm-fixture")
    monkeypatch.setenv("WORK2_COMM_WHEEL", str(wheel))
    monkeypatch.setattr(BUILD_PAGES, "COMM_WHEEL_SHA256", BUILD_PAGES._sha256(wheel))
    assert BUILD_PAGES._comm_wheel() == wheel.resolve()

    wheel.write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="SHA-256"):
        BUILD_PAGES._comm_wheel()


def test_offline_kernel_bootstrap_requires_comm_and_every_runtime_dependency() -> None:
    piplite = {"comm", "ipykernel", "piplite", "pyodide-kernel"}
    pyodide = {"ipython", "jedi", "micropip"}
    for pages_module in (BUILD_PAGES, CHECK_PAGES):
        pages_module._validate_kernel_bootstrap_packages(piplite, pyodide)
        with pytest.raises(RuntimeError, match="bootstrap packages.*comm"):
            pages_module._validate_kernel_bootstrap_packages(piplite - {"comm"}, pyodide)


def test_pages_source_projection_is_closed_world() -> None:
    assert BUILD_PAGES._publishable_source(Path("index.html"))
    assert BUILD_PAGES._publishable_source(
        Path("07-microstructure-reading-book/presentation/microstructure-reading-book-doc.html")
    )
    assert BUILD_PAGES._publishable_source(Path("14-avellaneda-stoikov/CAPSTONE.md"))
    assert not BUILD_PAGES._publishable_source(Path("package-lock.json"))
    assert not BUILD_PAGES._publishable_source(Path(".vscode/settings.json"))
    assert not BUILD_PAGES._publishable_source(
        Path("07-microstructure-reading-book/presentation/guion.md")
    )
    assert not BUILD_PAGES._publishable_source(
        Path("01-shadow/exercises/future-answer-key.ipynb")
    )
    assert not BUILD_PAGES._publishable_source(Path("15-final-exam/CLAUDE.md"))


def test_static_notebook_export_has_no_cdn_or_empty_runtime_scripts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "lesson/exercises/test.ipynb"
    source.parent.mkdir(parents=True)
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell(r"Una fórmula: $x^2$"),
        nbformat.v4.new_code_cell("print('offline')"),
    ])
    nbformat.write(notebook, source)
    output = tmp_path / "site"
    output.mkdir()
    monkeypatch.setattr(BUILD_PAGES, "ROOT", tmp_path)

    converted = BUILD_PAGES._convert_notebooks(
        output, {"notebooks": [Path("lesson/exercises/test.ipynb")]}
    )
    assert converted == [output / "lesson/exercises/test.html"]
    document = converted[0].read_text(encoding="utf-8")
    links = CHECK_PAGES.Links()
    links.feed(document)
    assert not [url for url in links.resource_urls if url.startswith(("http://", "https://"))]
    assert "cdnjs.cloudflare.com/ajax/libs/mermaid" not in document
    assert "do not load mermaidjs if not needed" not in document
    assert 'src=""' not in document and "src=''" not in document

    second_output = tmp_path / "second-site"
    second_output.mkdir()
    second = BUILD_PAGES._convert_notebooks(
        second_output, {"notebooks": [Path("lesson/exercises/test.ipynb")]}
    )[0]
    assert second.read_bytes() == converted[0].read_bytes()


def test_pages_builder_rejects_external_runtime_resources_before_promotion():
    with pytest.raises(RuntimeError, match="external runtime resource"):
        BUILD_PAGES._assert_offline_html(
            '<html><script src="https://cdn.example/runtime.js"></script></html>',
            "fixture.html",
        )


@pytest.mark.parametrize("resource", [
    '<object data="https://cdn.example/widget.html"></object>',
    '<embed src="//cdn.example/plugin.bin">',
    '<svg><image href="https://cdn.example/plot.svg"></image></svg>',
    (
        '<svg xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<image xlink:href="//cdn.example/plot.svg"></image></svg>'
    ),
    '<link rel="alternate manifest" href="https://cdn.example/app.webmanifest">',
])
def test_pages_reject_additional_browser_fetched_resources(resource: str) -> None:
    document = f"<html><head></head><body>{resource}</body></html>"
    with pytest.raises(RuntimeError, match="external runtime resource"):
        BUILD_PAGES._assert_offline_html(document, "fixture.html")

    links = CHECK_PAGES.Links()
    links.feed(document)
    assert CHECK_PAGES._external_runtime_urls(links)
    assert CHECK_PAGES._has_external_runtime_resource(document, links)


@pytest.mark.parametrize("call", [
    "fetch('https://cdn.example/runtime.json')",
    "fetch('https:' + '//cdn.example/runtime.json')",
    'new WebSocket("wss://stream.example/quotes")',
    "new WebSocket('wss:' + '//stream.example/quotes')",
    "new EventSource('//stream.example/events')",
    "import('https://cdn.example/runtime.mjs')",
    "importScripts('http://cdn.example/worker.js')",
])
def test_pages_reject_literal_dynamic_external_calls_inside_scripts(call: str) -> None:
    document = f"<html><body><script>{call}</script></body></html>"
    with pytest.raises(RuntimeError, match="external runtime resource"):
        BUILD_PAGES._assert_offline_html(document, "fixture.html")

    links = CHECK_PAGES.Links()
    links.feed(document)
    assert CHECK_PAGES._has_dynamic_external_call(links.inline_scripts)
    assert CHECK_PAGES._has_external_runtime_resource(document, links)


@pytest.mark.parametrize("surface", [
    '<meta http-equiv="refresh" content="5;url=https://outside.example/leak">',
    '<base href="https://outside.example/">',
    '<link rel="preconnect" href="https://outside.example">',
    '<link rel="dns-prefetch" href="//outside.example">',
    '<link rel="prefetch" href="https://outside.example/next">',
    '<link rel="prerender" href="https://outside.example/next">',
    '<img srcset="https://outside.example/a.png 1x">',
    '<link rel="preload" imagesrcset="https://outside.example/a.png 1x">',
    '<a href="./local.html" ping="https://outside.example/ping">local</a>',
    '<script>const endpoint="https://outside.example/x"; fetch(endpoint)</script>',
    '<script>new Worker("https://outside.example/worker.js")</script>',
    '<script>navigator.sendBeacon("https://outside.example/x", "x")</script>',
    '<script>new RTCPeerConnection({iceServers:[{urls:"stun:outside.example"}]})</script>',
    '<script>new XMLHttpRequest()</script>',
    '<script>new WebTransport("https://outside.example/session")</script>',
    '<script>navigator.serviceWorker.register("./worker.js")</script>',
    '<script>const ice="turns:outside.example:5349"</script>',
])
def test_pages_shared_policy_rejects_every_red_team_egress_surface(
    surface: str,
) -> None:
    document = f"<html><head></head><body>{surface}</body></html>"
    with pytest.raises(RuntimeError, match="external runtime resource"):
        BUILD_PAGES._assert_offline_html(document, "fixture.html")
    links = CHECK_PAGES.Links()
    links.feed(document)
    assert CHECK_PAGES._has_external_runtime_resource(document, links)


def test_pages_csp_is_canonical_first_and_checked_symmetrically() -> None:
    source = (
        '<!doctype html><html><head><meta charset="utf-8"></head>'
        '<body><a href="https://docs.example/reference">Referencia</a></body></html>'
    )
    hardened = OFFLINE_POLICY.inject_offline_csp(source, "fixture.html")
    assert hardened.count(OFFLINE_POLICY.CSP_META) == 1
    assert "connect-src 'self' data: blob:" in hardened
    OFFLINE_POLICY.validate_offline_html(
        hardened, "fixture.html", require_csp=True
    )
    assert not CHECK_PAGES._has_external_runtime_resource(
        hardened, CHECK_PAGES.Links()
    )

    for tampered in (
        source,
        hardened.replace("connect-src 'self'", "connect-src *"),
        hardened.replace(
            OFFLINE_POLICY.CSP_META,
            OFFLINE_POLICY.CSP_META + OFFLINE_POLICY.CSP_META,
        ),
        hardened.replace(
            "<head>\n" + OFFLINE_POLICY.CSP_META,
            "<head><script>void 0</script>" + OFFLINE_POLICY.CSP_META,
        ),
    ):
        with pytest.raises(RuntimeError, match="external runtime resource"):
            OFFLINE_POLICY.validate_offline_html(
                tampered, "fixture.html", require_csp=True
            )


def test_pages_allows_only_the_pinned_jupyterlite_local_redirect() -> None:
    local_redirect = r'''
      // redirect to /lab by default
      (function () {
        window.location.href = window.location.href.replace(
          /(\/|\/index.html)?(\?.*)$/,
          '/../../lab/index.html$2'
        );
      }.call(this));
    '''
    assert not OFFLINE_POLICY.inline_script_violations(local_redirect)

    external_redirect = local_redirect.replace(
        "'/../../lab/index.html$2'", "'https://outside.example/$2'"
    )
    assert "inline programmatic navigation" in (
        OFFLINE_POLICY.inline_script_violations(external_redirect)
    )


def _service_worker_fixture() -> tuple[bytes, bytes, str, str]:
    upstream = (
        b'"use strict";'
        + OFFLINE_POLICY.SERVICE_WORKER_UPSTREAM_ANCHOR
        + b'if("/health"===t.pathname)return;return e.respondWith(fetch(a))}'
    )
    hardened = upstream.replace(
        OFFLINE_POLICY.SERVICE_WORKER_UPSTREAM_ANCHOR,
        OFFLINE_POLICY.SERVICE_WORKER_HARDENED_ANCHOR,
    )
    return (
        upstream,
        hardened,
        hashlib.sha256(upstream).hexdigest(),
        hashlib.sha256(hardened).hexdigest(),
    )


def test_service_worker_hardening_requires_exact_bytes_guard_and_order() -> None:
    upstream, hardened, upstream_sha, hardened_sha = _service_worker_fixture()
    assert OFFLINE_POLICY.harden_service_worker_bytes(
        upstream,
        expected_upstream_sha256=upstream_sha,
        expected_hardened_sha256=hardened_sha,
    ) == hardened
    assert OFFLINE_POLICY.validate_hardened_service_worker_bytes(
        hardened, expected_hardened_sha256=hardened_sha
    ) == hardened_sha

    missing_anchor = upstream.replace(
        OFFLINE_POLICY.SERVICE_WORKER_UPSTREAM_ANCHOR, b"async function changed(){"
    )
    with pytest.raises(RuntimeError, match="anchor is not unique"):
        OFFLINE_POLICY.harden_service_worker_bytes(
            missing_anchor,
            expected_upstream_sha256=hashlib.sha256(missing_anchor).hexdigest(),
            expected_hardened_sha256=hardened_sha,
        )
    double_anchor = upstream + OFFLINE_POLICY.SERVICE_WORKER_UPSTREAM_ANCHOR
    with pytest.raises(RuntimeError, match="anchor is not unique"):
        OFFLINE_POLICY.harden_service_worker_bytes(
            double_anchor,
            expected_upstream_sha256=hashlib.sha256(double_anchor).hexdigest(),
            expected_hardened_sha256=hardened_sha,
        )


@pytest.mark.parametrize("mutation", [
    lambda payload: payload.replace(
        OFFLINE_POLICY.SERVICE_WORKER_EXTERNAL_GUARD, b""
    ),
    lambda payload: payload.replace(b"Response.error()", b"Response.redirect('/')"),
    lambda payload: payload.replace(
        OFFLINE_POLICY.SERVICE_WORKER_EXTERNAL_GUARD,
        OFFLINE_POLICY.SERVICE_WORKER_EXTERNAL_GUARD * 2,
    ),
    lambda payload: payload + b"// byte extra",
])
def test_service_worker_checker_rejects_absent_altered_double_or_extra_bytes(
    mutation,
) -> None:
    _upstream, hardened, _upstream_sha, hardened_sha = _service_worker_fixture()
    with pytest.raises(RuntimeError, match="bytes are not pinned"):
        OFFLINE_POLICY.validate_hardened_service_worker_bytes(
            mutation(hardened), expected_hardened_sha256=hardened_sha
        )


def test_service_worker_checker_rejects_guard_after_fetch_even_with_matching_sha() -> None:
    _upstream, hardened, _upstream_sha, _hardened_sha = _service_worker_fixture()
    misplaced = b"fetch(a);" + hardened
    with pytest.raises(RuntimeError, match="guard must precede every fetch"):
        OFFLINE_POLICY.validate_hardened_service_worker_bytes(
            misplaced,
            expected_hardened_sha256=hashlib.sha256(misplaced).hexdigest(),
        )


def test_pages_dynamic_call_guard_ignores_links_code_examples_and_local_fetches() -> None:
    document = """
    <html><body>
      <a href="https://docs.example/reference">Referencia</a>
      <pre>fetch('https://example.invalid/code-sample')</pre>
      <code>fetch('https:' + '//example.invalid/concatenated-sample')</code>
      <pre>&lt;object data="https://example.invalid/widget"&gt;&lt;/object&gt;</pre>
      <script>fetch('/algo_trading_intro/local.json')</script>
    </body></html>
    """
    BUILD_PAGES._assert_offline_html(document, "fixture.html")
    links = CHECK_PAGES.Links()
    links.feed(document)
    assert not CHECK_PAGES._has_dynamic_external_call(links.inline_scripts)
    assert not CHECK_PAGES._has_external_runtime_resource(document, links)


def test_jupyterlite_content_timestamps_are_canonical_and_enforced(tmp_path: Path) -> None:
    jupyter = tmp_path / "jupyter"
    metadata = jupyter / "api/contents/lesson/all.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text(json.dumps({
        "created": "2026-08-28T22:00:00Z",
        "last_modified": "2026-08-28T22:01:00Z",
        "content": [{
            "created": "2026-08-28T22:02:00Z",
            "last_modified": "2026-08-28T22:03:00Z",
        }],
    }), encoding="utf-8")

    assert BUILD_PAGES._canonicalize_jupyterlite_content_metadata(jupyter) == 1
    CHECK_PAGES._validate_jupyterlite_content_metadata(jupyter)
    normalized = json.loads(metadata.read_text(encoding="utf-8"))
    assert normalized["created"] == BUILD_PAGES.JUPYTERLITE_CANONICAL_TIMESTAMP
    assert normalized["content"][0]["last_modified"] == (
        BUILD_PAGES.JUPYTERLITE_CANONICAL_TIMESTAMP
    )

    normalized["content"][0]["created"] = "2026-08-28T22:04:00Z"
    metadata.write_text(json.dumps(normalized), encoding="utf-8")
    with pytest.raises(RuntimeError, match="not deterministic"):
        CHECK_PAGES._validate_jupyterlite_content_metadata(jupyter)


def test_pinned_pyodide_core_map_is_exact_and_hash_mismatch_fails(
    tmp_path: Path,
) -> None:
    manifest = BUILD_PAGES._load_public_manifest()
    pyodide = manifest["pyodide"]
    assert isinstance(pyodide, dict)
    core_files = pyodide["core_files"]
    assert isinstance(core_files, dict)
    assert set(core_files) == BUILD_PAGES.PYODIDE_CORE_FILE_NAMES
    assert len(core_files) == 13

    runtime = tmp_path / "pyodide"
    runtime.mkdir()
    module = runtime / "pyodide.mjs"
    module.write_bytes(b"pinned core fixture\n")
    exact = {"pyodide.mjs": BUILD_PAGES._sha256(module)}
    for pages_module in (BUILD_PAGES, CHECK_PAGES):
        pages_module._validate_core_files(runtime, exact)
        with pytest.raises(RuntimeError, match="core file failed SHA-256"):
            pages_module._validate_core_files(runtime, {"pyodide.mjs": "0" * 64})


def test_publication_destinations_reject_rendered_notebook_collision() -> None:
    for pages_module in (BUILD_PAGES, CHECK_PAGES):
        with pytest.raises(RuntimeError, match="colliding"):
            pages_module._validate_projection_destinations(
                [Path("lesson.html")],
                [Path("lesson.ipynb")],
                [Path("lesson.ipynb")],
            )


def test_pages_promotion_keeps_new_output_and_preserves_backup_on_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(BUILD_PAGES, "ROOT", tmp_path)
    output = tmp_path / "_site-audit"
    staging = tmp_path / ".staging"
    for directory, sentinel in ((output, "old"), (staging, "new")):
        directory.mkdir()
        (directory / BUILD_PAGES.OUTPUT_OWNER_FILE).write_text(
            json.dumps(BUILD_PAGES.OUTPUT_OWNER), encoding="utf-8"
        )
        (directory / f"{sentinel}.txt").write_text(sentinel, encoding="utf-8")

    def fail_cleanup(_path: Path) -> None:
        raise OSError("fixture cleanup failure")

    monkeypatch.setattr(BUILD_PAGES.shutil, "rmtree", fail_cleanup)
    with pytest.warns(RuntimeWarning, match="backup cleanup failed"):
        BUILD_PAGES._promote_output(staging, output)

    assert (output / "new.txt").read_text(encoding="utf-8") == "new"
    backups = list(tmp_path.glob("._site-audit.backup-*"))
    assert len(backups) == 1
    assert (backups[0] / "old.txt").read_text(encoding="utf-8") == "old"


def test_pages_output_safety_refuses_escape_symlinks_and_unowned_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(BUILD_PAGES, "ROOT", tmp_path)
    safe = tmp_path / "_site-audit"
    assert BUILD_PAGES._safe_output(safe) == safe
    for unsafe in (
        tmp_path / "nested" / "_site-audit",
        tmp_path.parent / "_site-outside",
        tmp_path / ".git",
    ):
        with pytest.raises(ValueError, match="unsafe output directory"):
            BUILD_PAGES._safe_output(unsafe)

    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "_site-linked"
    linked.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe output directory"):
        BUILD_PAGES._safe_output(linked)

    unowned = tmp_path / "_site-unowned"
    unowned.mkdir()
    sentinel = unowned / "keep.txt"
    sentinel.write_text("must survive\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="refusing to replace unowned"):
        BUILD_PAGES._validate_replacement_target(unowned)
    assert sentinel.read_text(encoding="utf-8") == "must survive\n"

    (unowned / BUILD_PAGES.OUTPUT_OWNER_FILE).write_text(
        json.dumps(BUILD_PAGES.OUTPUT_OWNER), encoding="utf-8"
    )
    BUILD_PAGES._validate_replacement_target(unowned)


def test_lab_staging_uses_only_declared_files_and_rejects_source_symlinks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(BUILD_PAGES, "ROOT", tmp_path)
    declared = Path("lesson/exercise.ipynb")
    source = tmp_path / declared
    source.parent.mkdir()
    source.write_text(json.dumps({"cells": []}), encoding="utf-8")
    rogue = source.parent / "future-answer-key.ipynb"
    rogue.write_text(json.dumps({"cells": []}), encoding="utf-8")
    contents = tmp_path / "contents"
    contents.mkdir()
    count, converted = BUILD_PAGES._stage_lab_contents(
        contents, {"lab_files": [declared], "notebooks": [declared]}
    )
    assert (count, converted) == (1, 0)
    assert (contents / declared).is_file()
    assert not (contents / rogue.relative_to(tmp_path)).exists()

    linked = Path("lesson/linked.ipynb")
    (tmp_path / linked).symlink_to(source.name)
    with pytest.raises(RuntimeError, match="must not be a symlink"):
        BUILD_PAGES._source_file(linked)


def _write_integrity_fixture(site: Path, manifest_path: Path) -> dict[str, object]:
    root = manifest_path.parents[2]
    source_payloads = {
        "index.html": b"<!doctype html><title>source fixture</title>\n",
        "lesson.ipynb": b'{"cells": []}\n',
    }
    for relative, payload in source_payloads.items():
        (root / relative).write_bytes(payload)
    files = {
        ".nojekyll": b"",
        CHECK_PAGES.OWNER_FILE: (json.dumps(CHECK_PAGES.EXPECTED_OWNER) + "\n").encode(),
        "index.html": b"<!doctype html><title>fixture</title>\n",
        "lesson.html": b"<!doctype html><title>lesson</title>\n",
        "jupyter/files/lesson.ipynb": b'{"cells": []}\n',
        "jupyter/jupyter-lite.json": b"{}\n",
        "jupyter/static/pyodide/pyodide.mjs": b"export {};\n",
    }
    for relative, payload in files.items():
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    build_input_payloads = {
        "framework/_build/build_pages.py": b"# fixture builder\n",
        "framework/_build/pages_offline_policy.py": b"# fixture offline policy\n",
        "package-lock.json": b'{}\n',
        "requirements-pages-lock.txt": b"fixture==1 --hash=sha256:" + b"a" * 64 + b"\n",
    }
    for relative, payload in build_input_payloads.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    manifest_path.write_text("fixture public manifest\n", encoding="utf-8")
    build_input_payloads["framework/_build/pages_public_manifest.json"] = (
        manifest_path.read_bytes()
    )
    build_inputs = [
        {
            "path": relative,
            "size": len(payload),
            "sha256": CHECK_PAGES._sha256(root / relative),
        }
        for relative, payload in sorted(build_input_payloads.items())
    ]
    records = [
        {"path": relative, "size": len(payload),
         "sha256": CHECK_PAGES._sha256(site / relative)}
        for relative, payload in sorted(files.items())
    ]
    pyodide_records = [
        record for record in records
        if record["path"].startswith("jupyter/static/pyodide/")
    ]
    core_hash = CHECK_PAGES._sha256(site / "jupyter/static/pyodide/pyodide.mjs")
    manifest: dict[str, object] = {
        "static_files": [Path("index.html")],
        "lab_files": [Path("lesson.ipynb")],
        "notebooks": [Path("lesson.ipynb")],
        "pyodide": {"archive_sha256": "a" * 64, "core_files": {"pyodide.mjs": core_hash}},
    }
    source_records = [
        {
            "path": relative,
            "size": len(payload),
            "sha256": CHECK_PAGES._sha256(root / relative),
        }
        for relative, payload in sorted(source_payloads.items())
    ]
    integrity = {
        "schema": 2,
        "hash_algorithm": "SHA-256",
        "github_sha": None,
        "build_inputs": build_inputs,
        "source_manifest_sha256": CHECK_PAGES._sha256(manifest_path),
        "source_files": source_records,
        "pyodide_archive_sha256": "a" * 64,
        "config": {
            "path": "jupyter/jupyter-lite.json",
            "sha256": next(record["sha256"] for record in records
                           if record["path"] == "jupyter/jupyter-lite.json"),
        },
        "pyodide_files": pyodide_records,
        "files": records,
    }
    (site / CHECK_PAGES.INTEGRITY_FILE).write_text(
        json.dumps(integrity), encoding="utf-8"
    )
    return manifest


def test_integrity_check_rejects_tampering_and_undeclared_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    site = tmp_path / "site"
    site.mkdir()
    manifest_path = tmp_path / "framework/_build/pages_public_manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = _write_integrity_fixture(site, manifest_path)
    monkeypatch.setattr(CHECK_PAGES, "PUBLIC_MANIFEST", manifest_path)
    monkeypatch.setattr(CHECK_PAGES, "ROOT", tmp_path)
    CHECK_PAGES._verify_integrity(site, manifest)

    source = tmp_path / "index.html"
    original_source = source.read_bytes()
    source.write_bytes(b"changed declared source\n")
    with pytest.raises(RuntimeError, match="declared source failed integrity"):
        CHECK_PAGES._verify_integrity(site, manifest)
    source.write_bytes(original_source)

    extra = site / "future-answer-key.html"
    extra.write_text("secret\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="file set differs"):
        CHECK_PAGES._verify_integrity(site, manifest)
    extra.unlink()

    build_input = tmp_path / "requirements-pages-lock.txt"
    original_build_input = build_input.read_bytes()
    build_input.write_bytes(b"tampered build lock\n")
    with pytest.raises(RuntimeError, match="build input failed integrity"):
        CHECK_PAGES._verify_integrity(site, manifest)
    build_input.write_bytes(original_build_input)

    (site / "index.html").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="failed integrity"):
        CHECK_PAGES._verify_integrity(site, manifest)


def test_pages_checker_rejects_a_declared_source_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_source = tmp_path / "real-index.html"
    real_source.write_text("fixture\n", encoding="utf-8")
    linked_source = tmp_path / "index.html"
    linked_source.symlink_to(real_source.name)
    records = [{
        "path": "index.html",
        "size": real_source.stat().st_size,
        "sha256": CHECK_PAGES._sha256(real_source),
    }]
    manifest: dict[str, object] = {
        "static_files": [Path("index.html")],
        "lab_files": [],
    }
    monkeypatch.setattr(CHECK_PAGES, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="provenance input must not be a symlink"):
        CHECK_PAGES._verify_source_records(records, manifest)


def test_pages_github_sha_provenance_binds_inputs_to_committed_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    sha = "1" * 40
    payloads = {
        path.as_posix(): f"fixture:{path.as_posix()}\n".encode()
        for path in BUILD_PAGES.BUILD_INPUT_PATHS
    }
    records = []
    for identity, payload in payloads.items():
        target = tmp_path / identity
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        records.append({
            "path": identity,
            "size": len(payload),
            "sha256": BUILD_PAGES._sha256(target),
        })
    source_payloads = {
        "index.html": b"<!doctype html><title>committed source</title>\n",
        "lesson.ipynb": b'{"cells": []}\n',
    }
    source_records = []
    for identity, payload in source_payloads.items():
        target = tmp_path / identity
        target.write_bytes(payload)
        payloads[identity] = payload
        source_records.append({
            "path": identity,
            "size": len(payload),
            "sha256": BUILD_PAGES._sha256(target),
        })
    source_manifest: dict[str, object] = {
        "static_files": [Path("index.html")],
        "lab_files": [Path("lesson.ipynb")],
    }

    mismatched: set[str] = set()

    def fake_git(command, **_kwargs):
        if command[1:3] == ["rev-parse", "--verify"]:
            return SimpleNamespace(stdout=f"{sha}\n".encode())
        assert command[1] == "show"
        identity = command[2].split(":", 1)[1]
        payload = b"different committed bytes\n" if identity in mismatched else payloads[identity]
        return SimpleNamespace(stdout=payload)

    monkeypatch.setattr(BUILD_PAGES, "ROOT", tmp_path)
    monkeypatch.setattr(CHECK_PAGES, "ROOT", tmp_path)
    monkeypatch.setattr(BUILD_PAGES.subprocess, "run", fake_git)
    monkeypatch.setenv("GITHUB_SHA", sha)
    assert BUILD_PAGES._validated_github_sha([*records, *source_records]) == sha
    assert CHECK_PAGES._verify_build_inputs(records, sha)
    CHECK_PAGES._verify_source_records(source_records, source_manifest, sha)

    mismatched.add("index.html")
    with pytest.raises(RuntimeError, match="differs from GITHUB_SHA"):
        BUILD_PAGES._validated_github_sha([*records, *source_records])
    with pytest.raises(RuntimeError, match="source differs from artifact GITHUB_SHA"):
        CHECK_PAGES._verify_source_records(source_records, source_manifest, sha)
    mismatched.clear()

    mismatched.add("package-lock.json")
    with pytest.raises(RuntimeError, match="differs from GITHUB_SHA"):
        BUILD_PAGES._validated_github_sha(records)
    with pytest.raises(RuntimeError, match="differs from artifact GITHUB_SHA"):
        CHECK_PAGES._verify_build_inputs(records, sha)


def test_pages_github_sha_provenance_rejects_malformed_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_SHA", "NOT-A-COMMIT")
    with pytest.raises(RuntimeError, match="40 lowercase hexadecimal"):
        BUILD_PAGES._validated_github_sha([])
    with pytest.raises(RuntimeError, match="40 lowercase hexadecimal"):
        CHECK_PAGES._verify_build_inputs([], None)


def test_link_resolver_fails_closed_on_artifact_and_base_path_escape(
    tmp_path: Path,
) -> None:
    site = tmp_path / "site"
    page = site / "lesson" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("fixture\n", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes the Pages artifact"):
        CHECK_PAGES.local_target(page, "../../../outside.txt", site, "/course/")
    with pytest.raises(ValueError, match="escapes Pages base path"):
        CHECK_PAGES.local_target(page, "/other/index.html", site, "/course/")
    for raw in (r"..\secret.txt", r"%5c%5cserver%5cshare%5cx"):
        with pytest.raises(ValueError, match="backslash"):
            CHECK_PAGES.local_target(page, raw, site, "/course/")


@pytest.mark.parametrize("raw", [r"..\secret", r"C:\secret", r"\\server\share\x"])
def test_manifest_paths_reject_non_posix_aliases(raw: str) -> None:
    with pytest.raises(RuntimeError, match="non-canonical"):
        BUILD_PAGES._manifest_relative(raw)
    with pytest.raises(RuntimeError, match="non-canonical"):
        CHECK_PAGES._manifest_relative(raw)


def test_pyodide_download_never_follows_a_preexisting_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = tmp_path / "algo-trading-pages-cache"
    cache.mkdir(mode=0o700)
    sentinel = tmp_path / "sentinel.bin"
    sentinel.write_bytes(b"preserve me")
    fixed_uuid = SimpleNamespace(hex="fixed")
    partial = cache / f".{BUILD_PAGES.PYODIDE_ARCHIVE}.fixed.partial"
    partial.symlink_to(sentinel)

    monkeypatch.delenv("WORK2_PYODIDE_ARCHIVE", raising=False)
    monkeypatch.setattr(BUILD_PAGES.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(BUILD_PAGES.uuid, "uuid4", lambda: fixed_uuid)
    with pytest.raises(FileExistsError):
        BUILD_PAGES._pyodide_archive()
    assert sentinel.read_bytes() == b"preserve me"


def test_pages_dependency_lock_is_exact_and_contains_every_direct_requirement() -> None:
    hash_pattern = re.compile(r"--hash=sha256:[0-9a-f]{64}")

    def requirements(path: Path, *, require_hashes: bool) -> dict[str, str]:
        records: dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            assert "==" in line and not any(token in line for token in (">=", "<=", "~=", "!="))
            hashes = hash_pattern.findall(line)
            if require_hashes:
                assert len(hashes) == 1, f"lock entry must have exactly one SHA-256: {line}"
                assert line.endswith(hashes[0]), f"unexpected lock syntax: {line}"
            else:
                assert not hashes, f"direct requirements should stay human-maintained: {line}"
            name, pinned = line.split("==", 1)
            pinned = pinned.split()[0]
            canonical = name.lower().replace("_", "-").replace(".", "-")
            assert canonical not in records
            records[canonical] = pinned
        return records

    direct = requirements(ROOT / "requirements-pages.txt", require_hashes=False)
    locked = requirements(ROOT / "requirements-pages-lock.txt", require_hashes=True)
    assert direct.items() <= locked.items()
    assert {"pytest", "overrides"} <= locked.keys()
    assert len(locked) == 66

    for workflow_name in ("course.yml", "pages.yml"):
        workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
        installs = [line for line in workflow.splitlines() if "pip install" in line]
        assert installs and all("--require-hashes" in line and "--only-binary=:all:" in line
                                for line in installs)


def test_pages_workflow_requires_two_checked_identical_builds_before_upload() -> None:
    workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    assert "build_pages.py --output _site\n" in workflow
    assert "build_pages.py --output _site-repro" in workflow
    assert "check_pages.py _site --base-path /algo_trading_intro/" in workflow
    assert "check_pages.py _site-repro --base-path /algo_trading_intro/" in workflow
    assert "cmp --silent _site/.pages-integrity.json _site-repro/.pages-integrity.json" in workflow

    upload = workflow[workflow.index("Compartir el site exacto"):workflow.index("\n  webkit-site:")]
    assert "path: _site\n" in upload
    assert "_site-repro" not in upload

    package = workflow[workflow.index("\n  package:"):workflow.index("\n  deploy:")]
    assert "github.event_name == 'workflow_dispatch'" in package
    assert "github.ref == 'refs/heads/main'" in package
    assert "inputs.publish" in package
    deploy = workflow[workflow.index("\n  deploy:"):]
    assert "group: pages-deploy" in deploy
    assert "cancel-in-progress: false" in deploy
