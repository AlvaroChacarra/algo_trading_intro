#!/usr/bin/env python3
"""check_my_work.py — corrige tu cuaderno desde la terminal.

Ejecuta las celdas de un cuaderno de ejercicios y cuenta cuántos validadores
(las celdas con la ✅ plegada) pasan, cuántos fallan y cuántos siguen sin tocar.
Así sabes cómo llevas la clase sin abrir Jupyter.

Uso:
    python check_my_work.py 4          # cuaderno de construcción de la clase 4
    python check_my_work.py 4 --aux    # el gimnasio (auxiliares) de la clase 4
    python check_my_work.py all        # todas las clases, de un vistazo

No necesita Jupyter: ejecuta las celdas en el propio Python (mismo criterio que
usa el generador del curso). Se salta las celdas mágicas (`!python`, `%…`).
"""

from __future__ import annotations

import glob
import io
import json
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = DIM = RESET = ""


def _lesson_dir(n: int) -> str | None:
    matches = sorted(glob.glob(os.path.join(HERE, f"{n:02d}-*")))
    return matches[0] if matches else None


def _notebook_path(n: int, aux: bool) -> str | None:
    d = _lesson_dir(n)
    if not d:
        return None
    kind = "auxiliary" if aux else "build_exercises"
    p = os.path.join(d, "exercises", f"{n:02d}_{kind}.ipynb")
    return p if os.path.exists(p) else None


def _is_magic(src: str) -> bool:
    for line in src.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s.startswith("!") or s.startswith("%")
    return False


def check_notebook(path: str) -> tuple[int, int, int, list[str]]:
    """Devuelve (pasan, fallan, sin_tocar, detalles_de_fallo)."""
    nb = json.load(open(path, encoding="utf-8"))
    ns: dict = {}
    passed = failed = untouched = 0
    fails: list[str] = []
    ex_title = "?"

    # ejecuta desde la carpeta del cuaderno: así `import exchange` / `order_book`
    # y las rutas a data/ resuelven igual que cuando el alumno lo abre.
    exdir = os.path.dirname(path)
    old_cwd, old_path = os.getcwd(), list(sys.path)
    os.chdir(exdir)
    sys.path.insert(0, exdir)
    try:
        return _run_cells(nb, path, ns)
    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_path


def _run_cells(nb: dict, path: str, ns: dict) -> tuple[int, int, int, list[str]]:
    passed = failed = untouched = 0
    fails: list[str] = []
    ex_title = "?"

    for cell in nb.get("cells", []):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            # recuerda el título del ejercicio en curso para los mensajes
            for line in src.splitlines():
                if line.startswith("### "):
                    ex_title = line[4:].strip()
                    break
            continue
        if cell.get("cell_type") != "code" or _is_magic(src):
            continue

        is_validator = "# ✅" in src
        try:
            with redirect_stdout(io.StringIO()):
                exec(compile(src, path, "exec"), ns)
            if is_validator:
                passed += 1
        except AssertionError as e:
            if not is_validator:
                continue
            msg = str(e)
            if msg.startswith("⏸"):
                untouched += 1
            else:
                failed += 1
                fails.append(f"{ex_title}: {msg or 'assert sin mensaje'}")
        except NameError:
            # el nombre que se pide aún no existe: ejercicio sin empezar
            if is_validator:
                untouched += 1
        except Exception as e:  # noqa: BLE001 — otros errores = respuesta rota
            if is_validator:
                failed += 1
                fails.append(f"{ex_title}: {type(e).__name__}: {e}")
    return passed, failed, untouched, fails


def _report_one(n: int, aux: bool) -> tuple[int, int, int]:
    path = _notebook_path(n, aux)
    label = f"Clase {n:02d} · {'gimnasio' if aux else 'construcción'}"
    if not path:
        print(f"{DIM}{label}: no encontrado{RESET}")
        return 0, 0, 0
    passed, failed, untouched, fails = check_notebook(path)
    total = passed + failed + untouched
    bar = (f"{GREEN}{passed}✓{RESET} · {RED}{failed}✗{RESET} · "
           f"{YELLOW}{untouched}⏸ sin tocar{RESET}  de {total}")
    print(f"{label}: {bar}")
    for f in fails[:8]:
        print(f"    {RED}✗{RESET} {f}")
    if len(fails) > 8:
        print(f"    {DIM}… y {len(fails) - 8} más{RESET}")
    return passed, failed, untouched


def main() -> None:
    args = sys.argv[1:]
    aux = "--aux" in args
    args = [a for a in args if a != "--aux"]
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("Uso: python check_my_work.py <clase|all> [--aux]")
        sys.exit(2)

    if args[0].lower() == "all":
        tp = tf = tu = 0
        for n in range(1, 15):
            p, f, u = _report_one(n, aux)
            tp += p; tf += f; tu += u
        print(f"\n{GREEN}{tp}✓{RESET} · {RED}{tf}✗{RESET} · {YELLOW}{tu}⏸{RESET} "
              f"en total ({'gimnasios' if aux else 'construcción'}).")
        sys.exit(1 if tf else 0)

    try:
        n = int(args[0])
    except ValueError:
        print(f"'{args[0]}' no es un número de clase válido (1-14) ni 'all'.")
        sys.exit(2)
    _, failed, _ = _report_one(n, aux)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
