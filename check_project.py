#!/usr/bin/env python3
"""Comprueba el proyecto acumulativo real: python check_project.py 10."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent


def check(through):
    package = ROOT / 'student_project' / 'exchange'
    if not package.is_dir():
        print('Primero prepara tu carpeta con course_workspace.py; consulta GUIA_LOCAL.md.')
        return 1
    sys.path.insert(0, str(package.parent))
    import exchange
    if Path(exchange.__file__).resolve() != package / '__init__.py':
        raise RuntimeError(f'paquete incorrecto: {exchange.__file__}')
    print(f'Tu código: {package}')
    failures = []
    for number in range(1, through + 1):
        candidates = sorted(ROOT.glob(f'{number:02d}-*/exercises/project_check.py'))
        if len(candidates) != 1:
            failures.append(f'L{number}: lección todavía no disponible en esta copia')
            continue
        try:
            path = candidates[0]
            exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), {'__name__':'__project_check__'})
            print(f'L{number:02d}: integración OK')
        except Exception as exc:
            failures.append(f'L{number:02d}: {type(exc).__name__}: {exc}')
    for failure in failures:
        print(failure)
    return 1 if failures else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', type=int, choices=range(1, 15))
    raise SystemExit(check(parser.parse_args().lesson))
