#!/usr/bin/env python3
"""Prepara/actualiza tu copia de estudio sin sobrescribir tu trabajo.

Desde la descarga del curso: python course_workspace.py ../mi-curso
Descarga una versión nueva y repite el mismo comando para añadir lecciones.
Los archivos que ya existen se conservan, incluso si cambia la distribución.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent


def update_workspace(source: Path, destination: Path) -> tuple[int, int]:
    source, destination = source.resolve(), destination.resolve()
    if destination == source or source in destination.parents or destination in source.parents:
        raise ValueError('elige una carpeta separada de la descarga del curso')
    files = []
    for pattern in ('[0-9][0-9]-*/exercises/**/*', 'student_project/**/*'):
        files.extend(p for p in source.glob(pattern) if p.is_file())
    files.extend(source / name for name in ('check_my_work.py', 'check_project.py', 'requirements.txt', 'GUIA_LOCAL.md')
                 if (source / name).is_file())
    added = preserved = 0
    for path in sorted(set(files)):
        if '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        target = destination / path.relative_to(source)
        if target.exists():
            preserved += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        added += 1
    package = destination / 'student_project' / 'exchange'
    package.mkdir(parents=True, exist_ok=True)
    init = package / '__init__.py'
    if not init.exists():
        init.write_text('"""Tu exchange: construido progresivamente, conservado entre clases."""\n')
    for starter in sorted(source.glob('[0-9][0-9]-*/exercises/project_starter/*.py')):
        target = package / starter.name
        if target.exists():
            preserved += 1
        else:
            shutil.copy2(starter, target)
            added += 1
    return added, preserved


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    added, preserved = update_workspace(ROOT, args.destination)
    print(f'{added} archivos añadidos; {preserved} existentes conservados. Abre {args.destination.resolve()}')
