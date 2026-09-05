"""Build Pages: the course index and released HTML presentations only.

Python, notebooks and data remain downloadable from the public repository.
The builder needs only the Python standard library.
"""
from __future__ import annotations

import argparse
import html
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


def student_html(document: str) -> str:
    """A folded instructor drawer is still public HTML: remove its payload."""
    return re.sub(r'<script\b[^>]*\bid="guion-src"[^>]*>.*?</script>', '', document, flags=re.S)


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
    parts = re.split(r'(<(?:script|style)\b[^>]*>.*?</(?:script|style)>)', document, flags=re.S | re.I)
    return ''.join(part if index % 2 else re.sub(r'''href=(["'])(.*?)\1''', replace, part)
                   for index, part in enumerate(parts))


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
