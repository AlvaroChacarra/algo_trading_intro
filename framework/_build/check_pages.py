"""Validate the presentation-only site, including partial course releases."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for name, value in attrs if name in {'href', 'src'} and value)


def local_target(page, raw, site, base_path):
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path)
    if path.startswith('/'):
        if not path.startswith(base_path):
            raise ValueError(f'link escapes Pages prefix: {raw}')
        path = path[len(base_path):]
        target = (site / path).resolve()
    else:
        target = (page.parent / path).resolve()
    if target != site and site not in target.parents:
        raise ValueError(f'link escapes output: {raw}')
    return target


def check(site, base_path='/algo_trading_intro/'):
    site = Path(site).resolve()
    failures = []
    if not (site / 'index.html').is_file():
        failures.append('missing index')
    for path in site.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(site)
        if path.suffix in {'.ipynb', '.py', '.wasm'} or 'jupyter' in rel.parts or 'exercises' in rel.parts:
            failures.append(f'non-presentation content: {rel}')
        if path.suffix != '.html':
            continue
        if rel != Path('index.html') and 'presentation' not in rel.parts:
            failures.append(f'HTML outside presentation: {rel}')
        text = path.read_text(encoding='utf-8')
        if 'name="viewport"' not in text and "name='viewport'" not in text:
            failures.append(f'missing viewport: {rel}')
        if re.search(r'<script\b[^>]*id="guion-src"', text):
            failures.append(f'instructor payload: {rel}')
        parser = Links()
        parser.feed(text)
        for url in parser.urls:
            try:
                target = local_target(path, url, site, base_path)
                if target is not None and not target.exists():
                    failures.append(f'{rel}: missing {url}')
            except ValueError as exc:
                failures.append(f'{rel}: {exc}')
    publication = site / '_publication.json'
    if publication.exists():
        released = json.loads(publication.read_text())['released_classes']
        index = (site / 'index.html').read_text()
        actual = set(re.findall(r'data-lesson="(\d{2})"', index))
        expected = {item['id'] for item in released}
        if actual != expected:
            failures.append(f'index lessons {actual} != release {expected}')
        for item in released:
            if not list((site / item['path'] / 'presentation').glob('*.html')):
                failures.append(f'missing released presentation: {item["id"]}')
    return failures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--base-path', default='/algo_trading_intro/')
    args = parser.parse_args()
    errors = check(args.site, args.base_path)
    print('\n'.join(errors) if errors else 'Pages: presentations and links OK')
    raise SystemExit(bool(errors))
