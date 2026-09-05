#!/usr/bin/env python3
"""Corrige notebooks locales: python check_my_work.py <clase|all> [--aux].

Cada notebook se ejecuta en un proceso limpio. Este comprobador rápido omite
magias de Jupyter; la aceptación docente en CI ejecuta también kernels reales.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from contextlib import redirect_stdout, redirect_stderr

HERE = Path(__file__).resolve().parent


def _is_magic(src: str) -> bool:
    return any(line.lstrip().startswith(('!', '%')) for line in src.splitlines())


def _run_cells(nb: dict, path: str, ns: dict) -> tuple[int, int, int, list[str]]:
    passed = failed = untouched = 0
    details = []
    title = '?'
    pending = False
    answer_error = None
    for number, cell in enumerate(nb.get('cells', []), 1):
        src = ''.join(cell.get('source', []))
        if cell.get('cell_type') == 'markdown':
            for line in src.splitlines():
                if line.startswith('### '):
                    title = line[4:].strip()
                    break
            continue
        if cell.get('cell_type') != 'code' or _is_magic(src):
            continue
        metadata = cell.get('metadata', {}).get('course', {})
        is_validator = metadata.get('role') == 'validator' or '# ✅' in src
        if metadata.get('role') == 'answer':
            pending = hashlib.sha256(src.encode()).hexdigest() == metadata.get('starter_sha256')
            answer_error = None
        if is_validator and answer_error:
            failed += 1
            details.append(f'{title}: ERROR DE EJECUCIÓN: {answer_error}')
            continue
        if is_validator and pending:
            untouched += 1
            continue
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exec(compile(src, f'{path}:celda {number}', 'exec'), ns)
            if is_validator:
                passed += 1
        except Exception as exc:
            message = f'celda {number}: {type(exc).__name__}: {exc}'
            if is_validator:
                if isinstance(exc, AssertionError) and str(exc).startswith('⏸'):
                    untouched += 1
                else:
                    failed += 1
                    kind = 'RESPUESTA INCORRECTA' if isinstance(exc, AssertionError) else 'ERROR DE EJECUCIÓN'
                    details.append(f'{title}: {kind}: {message}')
            elif metadata.get('role') == 'answer':
                answer_error = message
            else:
                failed += 1
                details.append(f'{title}: ERROR DE EJECUCIÓN: {message}')
    return passed, failed, untouched, details


def check_notebook(path: str) -> tuple[int, int, int, list[str]]:
    path = str(Path(path).resolve())
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), '--worker', path],
        cwd=Path(path).parent, text=True, capture_output=True, timeout=120,
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    passed, failed, untouched, details = json.loads(result.stdout)
    return passed, failed, untouched, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', nargs='?')
    parser.add_argument('--aux', action='store_true')
    parser.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        sys.path.insert(0, str(args.worker.parent))
        nb = json.loads(args.worker.read_text(encoding='utf-8'))
        print(json.dumps(_run_cells(nb, str(args.worker), {'__name__': '__main__'})))
        return 0
    if args.lesson is None:
        parser.error('indica una clase o all')
    kind = 'auxiliary' if args.aux else 'build_exercises'
    if args.lesson == 'all':
        paths = sorted(HERE.glob(f'[0-9][0-9]-*/exercises/*_{kind}.ipynb'))
    else:
        try:
            number = int(args.lesson)
        except ValueError:
            parser.error('la clase debe ser un número o all')
        paths = sorted(HERE.glob(f'{number:02d}-*/exercises/{number:02d}_{kind}.ipynb'))
    if not paths:
        parser.error('no hay notebooks disponibles para esa selección')
    failures = 0
    for path in paths:
        passed, failed, pending, details = check_notebook(str(path))
        print(f'{path.name}: {passed}✓ · {failed}✗ · {pending}⏸ pendientes')
        for detail in details:
            print('  ' + detail)
        failures += failed
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
