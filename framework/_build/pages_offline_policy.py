"""Shared fail-closed network policy for the generated Pages projection."""

from __future__ import annotations

import hashlib
import re
import stat
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


CSP_POLICY = (
    "default-src 'self' data: blob:; "
    "connect-src 'self' data: blob:; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' blob:; "
    "script-src-attr 'none'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "media-src 'self' data: blob:; "
    "worker-src 'self' blob:; "
    "child-src 'self' blob:; "
    "frame-src 'self' blob:; "
    "manifest-src 'self'; "
    "object-src 'none'; base-uri 'self'; form-action 'self'"
)
CSP_META = (
    '<meta http-equiv="Content-Security-Policy" '
    f'content="{CSP_POLICY}">'
)

OFFLINE_RUNTIME_GUARD_ID = "work2-offline-runtime-guard"
OFFLINE_RUNTIME_GUARD_STATE = "__WORK2_OFFLINE_GUARD__"
OFFLINE_RUNTIME_GUARD_BODY = r'''(()=>{"use strict";
let attempts=0;
const state=Object.freeze(Object.defineProperties({}, {
  attempts:{enumerable:true,get:()=>attempts}
}));
Object.defineProperty(globalThis,"__WORK2_OFFLINE_GUARD__",{
  value:state,writable:false,configurable:false,enumerable:false
});
const block=name=>{
  const denied=function(){
    attempts+=1;
    throw new DOMException("Offline policy blocked "+name,"SecurityError");
  };
  Object.defineProperty(globalThis,name,{
    value:denied,writable:false,configurable:false,enumerable:false
  });
};
["RTCPeerConnection","webkitRTCPeerConnection","open"].forEach(block);
})();'''
OFFLINE_RUNTIME_GUARD = (
    f'<script id="{OFFLINE_RUNTIME_GUARD_ID}">'
    f'{OFFLINE_RUNTIME_GUARD_BODY}</script>'
)
OFFLINE_HEAD_PREFIX = CSP_META + "\n" + OFFLINE_RUNTIME_GUARD

# JupyterLite 0.8.1 emits five small inline redirects for its lab and legacy
# route shims.  Their destinations are relative or derived exclusively from
# ``window.location`` and therefore stay on the current origin.  Pin the exact
# script bytes instead of broadly allowing location assignments: any upstream
# change, injected statement, or external destination fails closed.
PINNED_LOCAL_NAVIGATION_SCRIPT_SHA256 = frozenset({
    "81f42b11e586588d2a001d720793b20670466b11e4e71b7e0cc9941d36c58510",
    "a13c4f885dcfbf0c149fdfe51f53c5dac8de535d6baec96d2e911532233046ac",
    "a19b2e5a5892d6245bcae08627a0b89dc5941869f1e4f1f5778b5e298dc3aecf",
    "cc9bc1c71cd97202d85282c8dd6a6fac4d513de8a574b4b08e01876f14c8697a",
    "fd1b6a918c00c5790e2334870e36ecc49f246f6534e5f794db114b2313931121",
})

NETWORK_HINT_RELS = frozenset({
    "dns-prefetch", "preconnect", "prefetch", "prerender",
})
RESOURCE_LINK_RELS = frozenset({
    "stylesheet", "icon", "preload", "modulepreload", "manifest",
})
REMOTE_SCHEMES = frozenset({
    "http", "https", "ws", "wss", "stun", "turn", "turns",
})
CSS_REMOTE_RE = re.compile(
    r"(?:@import\s+(?:url\(\s*)?['\"]?|url\(\s*['\"]?)"
    r"(?:(?:https?|wss?):)?//",
    re.I,
)
STUN_TURN_RE = re.compile(r"\b(?:stun|turns?):", re.I)
INLINE_NETWORK_API_RE = re.compile(
    r"(?:"
    r"\b(?:importScripts|WebSocket|EventSource|SharedWorker|Worker|"
    r"(?:webkit)?RTCPeerConnection|XMLHttpRequest|WebTransport)\b"
    r"|\b(?:navigator\s*\.\s*)?(?:sendBeacon|serviceWorker)\b"
    r")",
    re.I,
)
DYNAMIC_IMPORT_RE = re.compile(r"\bimport\s*\(", re.I)
FETCH_CALL_RE = re.compile(r"\bfetch\s*\(", re.I)
PROGRAMMATIC_NAVIGATION_RE = re.compile(
    r"(?:"
    r"\b(?:window|globalThis|self|top|parent)\s*\.\s*open\b"
    r"|(?<![\w.$])open\s*\("
    r"|\b(?:(?:window|globalThis|self|top|parent|document)\s*\.\s*)?"
    r"location\s*(?:"
    r"=|\.\s*href\s*=|\.\s*(?:assign|replace)\s*\("
    r")"
    r")",
    re.I,
)
SAFE_LITERAL_ARGUMENT_RE = re.compile(
    r"\s*(['\"])([^'\"\\]*)\1\s*(?=,|\))", re.S
)
SIMPLE_STRING_CONCAT_RE = re.compile(
    r"(['\"])([^'\"\\\r\n]*)\1\s*\+\s*"
    r"(['\"])([^'\"\\\r\n]*)\3"
)
SIMPLE_BRACKET_PROPERTY_RE = re.compile(
    r"\[\s*(['\"])([A-Za-z_$][A-Za-z0-9_$]*)\1\s*\]"
)

SERVICE_WORKER_UPSTREAM_SHA256 = (
    "a8d6de96f77f4a0b73cf0fed10c76e78211659a05fa2222ba0a47e9a12f4eba9"
)
SERVICE_WORKER_HARDENED_SHA256 = (
    "f8b49c961f90bbcd7b8a3f61aa0c6fd551676a6c72d8fbe2d94aae38fd26f405"
)
SERVICE_WORKER_UPSTREAM_ANCHOR = (
    b"async function onFetch(e){let{request:a}=e,t=new URL(e.request.url);"
)
SERVICE_WORKER_EXTERNAL_GUARD = (
    b"if(t.origin!==self.location.origin)return void "
    b"e.respondWith(Response.error());"
)
SERVICE_WORKER_HARDENED_ANCHOR = (
    SERVICE_WORKER_UPSTREAM_ANCHOR + SERVICE_WORKER_EXTERNAL_GUARD
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_remote_url(raw: str) -> bool:
    split = urlsplit(raw.strip())
    return bool(split.netloc or split.scheme.lower() in REMOTE_SCHEMES)


def _literal_call_is_safe(script: str, open_paren_end: int) -> bool:
    """Allow only a direct, non-remote single/double-quoted URL argument."""
    match = SAFE_LITERAL_ARGUMENT_RE.match(script, open_paren_end)
    return bool(match and not _is_remote_url(match.group(2)))


def _quote_simple_javascript_string(value: str) -> str | None:
    """Return an escape-free JS literal when one can represent ``value``."""
    if "'" not in value and "\r" not in value and "\n" not in value:
        return f"'{value}'"
    if '"' not in value and "\r" not in value and "\n" not in value:
        return f'"{value}"'
    return None


def normalize_simple_javascript(script: str) -> str:
    """Fold bounded, escape-free literal concatenation and bracket properties.

    This deliberately covers common accidental/low-effort obfuscation. It is
    not a parser and must not be presented as proof against arbitrary hostile
    JavaScript.
    """
    normalized = script
    for _ in range(16):
        changed = False

        def fold(match: re.Match[str]) -> str:
            nonlocal changed
            replacement = _quote_simple_javascript_string(
                match.group(2) + match.group(4)
            )
            if replacement is None:
                return match.group(0)
            changed = True
            return replacement

        folded = SIMPLE_STRING_CONCAT_RE.sub(fold, normalized)
        if not changed:
            normalized = folded
            break
        normalized = folded
    return SIMPLE_BRACKET_PROPERTY_RE.sub(r".\2", normalized)


def _javascript_code_mask(script: str) -> str:
    """Keep executable JS tokens, blanking strings/comments but scanning ${...}."""
    output = [" "] * len(script)

    def quoted(index: int, quote: str) -> int:
        index += 1
        while index < len(script):
            if script[index] == "\\":
                index += 2
            elif script[index] == quote:
                return index + 1
            else:
                index += 1
        return index

    def template(index: int) -> int:
        index += 1
        while index < len(script):
            if script[index] == "\\":
                index += 2
            elif script[index] == "`":
                return index + 1
            elif script.startswith("${", index):
                index = code(index + 2, stop_at_template_brace=True)
            else:
                index += 1
        return index

    def code(index: int, *, stop_at_template_brace: bool = False) -> int:
        brace_depth = 0
        while index < len(script):
            character = script[index]
            if stop_at_template_brace and character == "}" and brace_depth == 0:
                return index + 1
            if character in {"'", '"'}:
                index = quoted(index, character)
                continue
            if character == "`":
                index = template(index)
                continue
            if script.startswith("//", index):
                newline = script.find("\n", index + 2)
                index = len(script) if newline < 0 else newline
                continue
            if script.startswith("/*", index):
                end = script.find("*/", index + 2)
                index = len(script) if end < 0 else end + 2
                continue
            output[index] = character
            if stop_at_template_brace:
                if character == "{":
                    brace_depth += 1
                elif character == "}":
                    brace_depth -= 1
            index += 1
        return index

    code(0)
    return "".join(output)


def inline_script_violations(script: str) -> list[str]:
    violations: list[str] = []
    normalized = normalize_simple_javascript(script)
    executable = _javascript_code_mask(normalized)
    if INLINE_NETWORK_API_RE.search(executable):
        violations.append("inline network-capable API")
    if (PROGRAMMATIC_NAVIGATION_RE.search(executable)
            and _sha256_bytes(script.encode("utf-8"))
            not in PINNED_LOCAL_NAVIGATION_SCRIPT_SHA256):
        violations.append("inline programmatic navigation")
    if STUN_TURN_RE.search(normalized):
        violations.append("inline STUN/TURN endpoint")
    for match in FETCH_CALL_RE.finditer(executable):
        if not _literal_call_is_safe(normalized, match.end()):
            violations.append("computed or remote fetch")
            break
    for match in DYNAMIC_IMPORT_RE.finditer(executable):
        if not _literal_call_is_safe(normalized, match.end()):
            violations.append("computed or remote dynamic import")
            break
    return violations


class OfflineHTMLParser(HTMLParser):
    """Collect browser-active surfaces while preserving ordinary hyperlinks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.resource_urls: list[str] = []
        self.inline_scripts: list[str] = []
        self.runtime_guards: list[str] = []
        self.csp_values: list[str] = []
        self.violations: list[str] = []
        self._script_chunks: list[str] | None = None
        self._script_is_runtime_guard = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.lower()
        attributes: dict[str, str | None] = {}
        for name, value in attrs:
            normalized_name = name.lower()
            if normalized_name in attributes:
                self.violations.append("duplicated HTML attribute")
            else:
                attributes[normalized_name] = value
            if normalized_name.startswith("on"):
                self.violations.append("inline event-handler attribute")
            if normalized_name == "srcdoc":
                self.violations.append("iframe srcdoc")
            if (isinstance(value, str)
                    and value.lstrip().lower().startswith("javascript:")):
                self.violations.append("javascript URL")
        rels = set((attributes.get("rel") or "").lower().split())

        if normalized_tag == "meta":
            http_equiv = (attributes.get("http-equiv") or "").strip().lower()
            if http_equiv == "refresh":
                self.violations.append("meta refresh")
            elif http_equiv == "content-security-policy":
                self.csp_values.append(attributes.get("content") or "")
        if normalized_tag == "base":
            self.violations.append("base element")
        if normalized_tag == "link" and rels & NETWORK_HINT_RELS:
            self.violations.append("network hint link")
        if "srcset" in attributes or "imagesrcset" in attributes:
            self.violations.append("responsive remote-capable source set")
        if "ping" in attributes:
            self.violations.append("hyperlink ping")

        resource_attributes: list[str | None] = []
        if normalized_tag in {
            "script", "img", "audio", "video", "source", "track", "iframe",
            "embed", "portal",
        }:
            resource_attributes.extend([
                attributes.get("src"), attributes.get("poster"),
            ])
        elif normalized_tag == "input" and (
            attributes.get("type") or ""
        ).lower() == "image":
            resource_attributes.append(attributes.get("src"))
        elif normalized_tag == "object":
            resource_attributes.append(attributes.get("data"))
        elif normalized_tag == "image":
            resource_attributes.extend([
                attributes.get("href"), attributes.get("xlink:href"),
            ])
        elif normalized_tag == "link" and rels & RESOURCE_LINK_RELS:
            resource_attributes.append(attributes.get("href"))
        self.resource_urls.extend(raw for raw in resource_attributes if raw)

        script_type = (attributes.get("type") or "").strip().lower()
        executable_script = (
            not script_type
            or script_type == "module"
            or script_type in {
                "text/javascript", "application/javascript",
                "text/ecmascript", "application/ecmascript",
            }
        )
        if (normalized_tag == "script" and not attributes.get("src")
                and executable_script):
            self._script_chunks = []
            self._script_is_runtime_guard = (
                attributes.get("id") == OFFLINE_RUNTIME_GUARD_ID
            )
        elif (normalized_tag == "script"
              and attributes.get("id") == OFFLINE_RUNTIME_GUARD_ID):
            self.violations.append("malformed offline runtime guard")

    def handle_data(self, data: str) -> None:
        if self._script_chunks is not None:
            self._script_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._script_chunks is not None:
            script = "".join(self._script_chunks)
            if self._script_is_runtime_guard:
                self.runtime_guards.append(script)
            else:
                self.inline_scripts.append(script)
            self._script_chunks = None
            self._script_is_runtime_guard = False


def offline_html_violations(
    document: str, *, require_csp: bool = False
) -> list[str]:
    parser = OfflineHTMLParser()
    parser.feed(document)
    violations = list(parser.violations)
    if any(_is_remote_url(raw) for raw in parser.resource_urls):
        violations.append("external runtime URL")
    if CSS_REMOTE_RE.search(document):
        violations.append("external CSS URL")
    if STUN_TURN_RE.search(document):
        violations.append("STUN/TURN endpoint")
    for script in parser.inline_scripts:
        violations.extend(inline_script_violations(script))

    if require_csp:
        if parser.csp_values != [CSP_POLICY]:
            violations.append("missing, duplicated, or altered CSP")
        if parser.runtime_guards != [OFFLINE_RUNTIME_GUARD_BODY]:
            violations.append("missing, duplicated, or altered offline runtime guard")
        if (document.count(CSP_META) != 1
                or document.count(OFFLINE_RUNTIME_GUARD) != 1):
            violations.append("offline hardening bytes are not exact")
        head_prefix = re.search(
            r"(?i:<head\b[^>]*>)\s*" + re.escape(OFFLINE_HEAD_PREFIX),
            document,
        )
        if head_prefix is None:
            violations.append("CSP/guard are not the first elements in head")
    # A canonical runtime guard is part of an already-hardened artifact, not
    # an egress surface.  ``inject_offline_csp`` independently refuses any
    # pre-existing CSP/guard before transforming source HTML, while
    # ``require_csp=True`` verifies the exact guard and its position in final
    # artifacts.  Treating it as an offline violation here made the generic
    # checker reject the very artifact produced by the builder.
    return violations


def validate_offline_html(
    document: str, label: str, *, require_csp: bool = False
) -> None:
    violations = offline_html_violations(document, require_csp=require_csp)
    if violations:
        summary = ", ".join(dict.fromkeys(violations))
        raise RuntimeError(f"external runtime resource in {label}: {summary}")


def inject_offline_csp(document: str, label: str) -> str:
    parser = OfflineHTMLParser()
    parser.feed(document)
    if parser.csp_values or parser.runtime_guards:
        raise RuntimeError(f"refusing pre-existing offline hardening in {label}")
    hardened, count = re.subn(
        r"(<head\b[^>]*>)", r"\1\n" + OFFLINE_HEAD_PREFIX, document,
        count=1, flags=re.I,
    )
    if count != 1:
        raise RuntimeError(f"HTML document has no unique head for CSP: {label}")
    validate_offline_html(hardened, label, require_csp=True)
    return hardened


def harden_service_worker_bytes(
    payload: bytes,
    *,
    expected_upstream_sha256: str = SERVICE_WORKER_UPSTREAM_SHA256,
    expected_hardened_sha256: str = SERVICE_WORKER_HARDENED_SHA256,
) -> bytes:
    """Transform only the one pinned upstream worker into the pinned safe worker."""
    if _sha256_bytes(payload) != expected_upstream_sha256:
        raise RuntimeError("JupyterLite service worker upstream bytes are not pinned")
    if payload.count(SERVICE_WORKER_UPSTREAM_ANCHOR) != 1:
        raise RuntimeError("JupyterLite service worker upstream anchor is not unique")
    if SERVICE_WORKER_EXTERNAL_GUARD in payload:
        raise RuntimeError("JupyterLite service worker was already or partially hardened")
    hardened = payload.replace(
        SERVICE_WORKER_UPSTREAM_ANCHOR, SERVICE_WORKER_HARDENED_ANCHOR, 1
    )
    validate_hardened_service_worker_bytes(
        hardened, expected_hardened_sha256=expected_hardened_sha256
    )
    return hardened


def validate_hardened_service_worker_bytes(
    payload: bytes,
    *,
    expected_hardened_sha256: str = SERVICE_WORKER_HARDENED_SHA256,
) -> str:
    """Require the complete transformed bytes and guard ordering, not a substring."""
    digest = _sha256_bytes(payload)
    if digest != expected_hardened_sha256:
        raise RuntimeError("JupyterLite hardened service worker bytes are not pinned")
    if (payload.count(SERVICE_WORKER_HARDENED_ANCHOR) != 1
            or payload.count(SERVICE_WORKER_EXTERNAL_GUARD) != 1):
        raise RuntimeError("JupyterLite service worker external-origin guard is not exact")
    guard_at = payload.find(SERVICE_WORKER_EXTERNAL_GUARD)
    first_fetch = payload.find(b"fetch(")
    if first_fetch < 0 or guard_at < 0 or guard_at > first_fetch:
        raise RuntimeError("JupyterLite service worker guard must precede every fetch")
    return digest


def _regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"{label} must be a regular non-symlink file")
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise RuntimeError(f"{label} must be a regular non-symlink file")
    return path.read_bytes()


def harden_service_worker(path: Path) -> str:
    payload = _regular_bytes(path, "JupyterLite service worker")
    hardened = harden_service_worker_bytes(payload)
    path.write_bytes(hardened)
    return SERVICE_WORKER_HARDENED_SHA256


def validate_hardened_service_worker(path: Path) -> str:
    payload = _regular_bytes(path, "JupyterLite service worker")
    return validate_hardened_service_worker_bytes(payload)
