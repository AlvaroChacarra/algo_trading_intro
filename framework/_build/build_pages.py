"""Build Pages: the course index and released HTML presentations only.

Python, notebooks and data remain downloadable from the public repository.
The builder needs only the Python standard library.
"""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = 'https://github.com/AlvaroChacarra/algo_trading_intro'
ASSETS = {'.css', '.js', '.png', '.jpg', '.svg', '.webp', '.woff2', '.woff', '.ttf'}


def _safe_output(path: Path) -> Path:
    output = path.resolve()
    if output == ROOT or output in ROOT.parents or output == Path('/'):
        raise ValueError(f'unsafe output directory: {output}')
    if output.exists() and any(output.iterdir()) and not (output / '.course-pages').is_file():
        raise ValueError('output no vacío y no creado por este builder')
    return output


class _RawTextSpans(HTMLParser):
    """Locate real HTML raw-text elements without serializing their contents.

    HTMLParser normalizes tag/attribute names and decodes attribute entities.
    Offsets let us preserve every byte of student JavaScript, including template
    strings that themselves contain HTML or references to ``guion-src``.
    """
    def __init__(self, document: str):
        super().__init__(convert_charrefs=False)
        self.document = document
        self.lines = [0]
        self.lines.extend(match.end() for match in re.finditer('\n', document))
        self.active = None
        self.spans = []

    def absolute_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'} and self.active is None:
            teacher = tag == 'script' and any(
                name == 'id' and value and value.casefold() == 'guion-src'
                for name, value in attrs
            )
            self.active = (self.absolute_offset(), tag, teacher)

    def handle_startendtag(self, tag, attrs):
        # In HTML, <script .../> is NOT a self-closing script element.
        self.handle_starttag(tag, attrs)
        if tag in {'script', 'style'}:
            self.set_cdata_mode(tag)

    def handle_endtag(self, tag):
        if self.active is not None and tag == self.active[1]:
            start, _, teacher = self.active
            end = self.document.find('>', self.absolute_offset()) + 1
            self.spans.append((start, end, teacher))
            self.active = None


def _raw_text_spans(document: str):
    parser = _RawTextSpans(document)
    parser.feed(document)
    parser.close()
    if parser.active is not None:
        start, _, teacher = parser.active
        # An unterminated teacher payload is never a publishable document.
        if teacher:
            raise ValueError('unterminated instructor payload: guion-src')
        parser.spans.append((start, len(document), False))
    return parser.spans


def has_instructor_payload(document: str) -> bool:
    return any(teacher for _, _, teacher in _raw_text_spans(document))


def student_html(document: str) -> str:
    """Remove only instructor script spans, preserving student scripts exactly."""
    parts, offset = [], 0
    for start, end, teacher in _raw_text_spans(document):
        if teacher:
            parts.append(document[offset:start])
            offset = end
    parts.append(document[offset:])
    return ''.join(parts)


def _links(document: str, relative: Path, root: Path) -> str:
    def replace(match):
        quote, raw = match.group(1), html.unescape(match.group(2))
        split = urlsplit(raw)
        if split.scheme or split.netloc or not split.path:
            return match.group(0)
        target = (root / relative.parent / unquote(split.path)).resolve()
        try:
            target_rel = target.relative_to(root.resolve())
        except ValueError:
            raise ValueError(f'link escapes course root: {relative}: {raw}')
        if target_rel.name == 'index.html' or ('presentation' in target_rel.parts and target.suffix == '.html'):
            return match.group(0)
        if target.suffix == '.html' and 'exercises' in target_rel.parts:
            target_rel = target_rel.with_suffix('.ipynb')
        destination = f'{PUBLIC}/blob/main/{target_rel.as_posix()}'
        if target_rel.suffix == '.ipynb':
            destination = f'{PUBLIC}/raw/refs/heads/main/{target_rel.as_posix()}'
        return f'href={quote}{html.escape(destination, quote=True)}{quote}'
    # Inline JavaScript contains template strings with href=; leave raw text intact.
    parts, offset = [], 0
    for start, end, _ in _raw_text_spans(document):
        parts.append(re.sub(r'''href=(["'])(.*?)\1''', replace, document[offset:start]))
        parts.append(document[start:end])
        offset = end
    parts.append(re.sub(r'''href=(["'])(.*?)\1''', replace, document[offset:]))
    return ''.join(parts)


def build(output: Path) -> int:
    output = _safe_output(output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / '.course-pages').touch()
    sources = [ROOT / 'index.html'] + sorted(ROOT.glob('[0-9][0-9]-*/presentation/*.html'))
    for source in sources:
        relative = source.relative_to(ROOT)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        document = _links(student_html(source.read_text(encoding='utf-8')), relative, ROOT)
        if relative != Path('index.html') and 'class="course-home"' not in document:
            home = os.path.relpath(output / 'index.html', destination.parent).replace(os.sep, '/')
            document = document.replace('</body>', f'<a class="course-home" href="{home}">← Curso</a></body>')
        destination.write_text(document, encoding='utf-8')
        for asset in source.parent.iterdir():
            if asset.is_file() and asset.suffix in ASSETS:
                shutil.copy2(asset, destination.parent / asset.name)
    if (ROOT / '_publication.json').is_file():
        shutil.copy2(ROOT / '_publication.json', output / '_publication.json')
    (output / '.nojekyll').touch()
    return len(sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    print(f'Pages: {build(args.output)} index/presentation HTML files')
