"""build_course.py — genera las lecciones L1-L14 desde los specs.

1. Autovalida cada ejercicio: exec(given + solution + validator) con el paquete
   de referencia en el path. Si algo falla, NO emite nada.
2. Emite por lección: README, CLAUDE, presentation/(html+guion),
   exercises/(build nb + aux nb + paquete exchange acumulado), data/.

Uso:  python build_course.py [--check-only]
"""

from __future__ import annotations

import os
import shutil
import sys
import traceback

HERE = os.path.dirname(__file__)
FRAMEWORK = os.path.dirname(HERE)            # .../framework
ROOT = os.path.dirname(FRAMEWORK)            # .../algo_trading_intro
sys.path.insert(0, FRAMEWORK)               # para importar 'exchange'
sys.path.insert(0, HERE)

import nbgen  # noqa: E402
from lessons_foundations import LESSONS as L_FOUND  # noqa: E402
from lessons_engine import LESSONS as L_ENG  # noqa: E402
from lessons_strategies import LESSONS as L_STRAT  # noqa: E402
from lessons_docs import DOCS  # noqa: E402

LESSONS = L_FOUND + L_ENG + L_STRAT
EXCHANGE_SRC = os.path.join(FRAMEWORK, "exchange")


# ---------------------------------------------------------------------------
# 1) Autovalidación
# ---------------------------------------------------------------------------

def self_test() -> list[str]:
    failures = []
    for lesson in LESSONS:
        for kind in ("build", "aux"):
            for ex in lesson.get(kind, []):
                ns: dict = {}
                code = (ex.get("given", "") + "\n" + ex["solution"]
                        + "\n" + ex["validator"])
                try:
                    exec(compile(code, f"L{lesson['n']}:{ex['title']}", "exec"), ns)
                except Exception:
                    failures.append(
                        f"L{lesson['n']} [{kind}] {ex['title']}\n"
                        + traceback.format_exc())
    return failures


# ---------------------------------------------------------------------------
# 2) Staging del paquete acumulado
# ---------------------------------------------------------------------------

def modules_for(n: int):
    core, strat, top = [], [], []
    if n >= 3:
        core += ["orders.py", "trades.py"]
        top += [("orders", "Order, Side, OrderType"), ("trades", "Fill")]
    if n >= 4:
        core += ["book.py", "portfolio.py"]
        top += [("book", "OrderBook, Level"), ("portfolio", "PositionTracker")]
    if n >= 5:
        core += ["matching.py", "market.py"]
        top += [("matching", "MatchingEngine"), ("market", "Market")]
    if n >= 8:
        core += ["strategy.py", "backtest.py"]
        top += [("strategy", "Strategy, NewOrder, Cancel, Action"),
                ("backtest", "Backtest, BacktestResult")]
    if n >= 10:
        strat += [("vwap", "VWAPStrategy")]
    if n >= 12:
        strat += [("market_maker", "MarketMaker, AvellanedaStoikov")]
        core += ["simulation.py"]
    return core, strat, top


def stage_package(n: int, dest_exercises: str) -> bool:
    core, strat, top = modules_for(n)
    if not (core or strat):
        return False
    pkg = os.path.join(dest_exercises, "exchange")
    os.makedirs(pkg, exist_ok=True)

    for f in core:
        shutil.copy(os.path.join(EXCHANGE_SRC, f), os.path.join(pkg, f))
    if n >= 5:  # datos para Market.sample()
        data_dst = os.path.join(pkg, "_data")
        os.makedirs(data_dst, exist_ok=True)
        shutil.copy(os.path.join(EXCHANGE_SRC, "_data", "btc_lob_snapshots.csv"),
                    os.path.join(data_dst, "btc_lob_snapshots.csv"))

    # __init__ raíz del paquete (solo símbolos presentes)
    lines = ['"""exchange — paquete del curso (acumulado hasta esta clase)."""\n']
    for mod, syms in top:
        lines.append(f"from exchange.{mod} import {syms}")
    with open(os.path.join(pkg, "__init__.py"), "w") as f:
        f.write("\n".join(lines) + "\n")

    # subpaquete strategies
    if strat:
        sdir = os.path.join(pkg, "strategies")
        os.makedirs(sdir, exist_ok=True)
        for mod, _ in strat:
            shutil.copy(os.path.join(EXCHANGE_SRC, "strategies", f"{mod}.py"),
                        os.path.join(sdir, f"{mod}.py"))
        sinit = []
        for mod, syms in strat:
            sinit.append(f"from exchange.strategies.{mod} import {syms}")
        with open(os.path.join(sdir, "__init__.py"), "w") as f:
            f.write("\n".join(sinit) + "\n")
    return True


# ---------------------------------------------------------------------------
# 3) Documentos por lección
# ---------------------------------------------------------------------------

def tiers_md(kind: str) -> str:
    if kind == "build":
        return ("### Cómo funciona este cuaderno\n\n"
                "1. Escribe tu respuesta en la celda de código.\n"
                "2. Debajo hay una **✅ comprobación plegada**: ejecútala con `Shift+Enter` para validarte "
                "(despliégala si quieres ver el `assert`).\n"
                "3. ¿Atascado? Abre **💡 Ver solución**.\n\n"
                "**Núcleo:** ej. 1–3 · **Si vamos bien:** el resto · **Más:** el cuaderno de auxiliares.")
    return ("### Auxiliares\n\n"
            "Profundización opcional, mismo formato: comprobación plegada + solución desplegable. "
            "No hacen falta para seguir el curso.")


def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text)


def readme(lesson: dict, has_pkg: bool) -> str:
    doc = DOCS.get(lesson["n"], {})
    pkg_line = ("- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)\n"
                if has_pkg else "")
    build = "\n".join(f"- **{ex['title']}** — {ex['practice']}" for ex in lesson["build"])
    return (f"# Clase {lesson['n']} — {lesson['title']}\n\n"
            f"> {lesson['objective']}\n\n"
            f"## Contexto teórico\n\n{doc.get('theory', '')}\n\n"
            f"## Qué construyes hoy\n\n**{lesson['piece']}**\n\n"
            f"{doc.get('technical', '')}\n\n"
            f"## Ejercicios de construcción\n\n{build}\n\n"
            f"## Estructura de la carpeta\n\n"
            f"- `presentation/` — presentación interactiva + guion del profesor\n"
            f"- `exercises/{lesson['n']:02d}_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)\n"
            f"- `exercises/{lesson['n']:02d}_auxiliary.ipynb` — profundización opcional\n"
            f"{pkg_line}\n"
            f"## Idea central\n\n> {_strip_html(lesson['frase'])}\n")


def claude_md(lesson: dict, has_pkg: bool) -> str:
    doc = DOCS.get(lesson["n"], {})
    blocks = "\n".join(f"{i}. **{b[0]}** — {b[1]}" for i, b in enumerate(lesson["concepts"], 1))
    return (f"# Clase {lesson['n']} — {lesson['title']} (guía de implementación)\n\n"
            f"Pieza del framework: **{lesson['piece']}**.\n\n"
            f"## Teoría que cubre\n\n{doc.get('theory', '')}\n\n"
            f"## Implementación técnica\n\n{doc.get('technical', '')}\n\n"
            f"## Presentación (3 bloques)\n\n{blocks}\n\n"
            f"## Cuaderno de construcción\n\n"
            f"Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con "
            f"mensaje claro, tolerancia `1e-9`) → solución guiada embebida.\n"
            f"Tiers: **Núcleo** = ej. 1-3 (en clase), **Si vamos bien** = resto, **Auxiliares** = "
            f"cuaderno `{lesson['n']:02d}_auxiliary.ipynb`.\n\n"
            f"El contenido se genera desde `framework/_build/` — para editar esta clase, edita su "
            f"spec y regenera con `build_course.py`. No edites a mano los notebooks.\n\n"
            f"## Continuidad\n\n"
            f"{'El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.' if has_pkg else 'Aún sin paquete: las clases se construyen en celdas del notebook (estilo L1-L2). El vocabulario de hoy se convierte en los atributos de las clases en L3.'}\n")


def guion_md(lesson: dict) -> str:
    out = [f"# Guion — Clase {lesson['n']}: {lesson['title']}\n",
           f"**Idea central:** {lesson['frase']}\n",
           "Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.\n"]
    for i, (h, body, _snip) in enumerate(lesson["concepts"], 1):
        out.append(f"\n## Bloque {i}: {h}\n")
        out.append(f"- **Qué decir:** {body}")
        out.append(f"- **Acción en pantalla:** mostrar el snippet del bloque {i} y ejecutarlo en el notebook.")
    out.append("\n## Cierre\n- Recoge la idea central y manda abrir `exercises/`.")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 4) Emisión
# ---------------------------------------------------------------------------

def closing_build(lesson: dict) -> str:
    nxt = lesson["n"] + 1
    return (f"## Cierre\n\n{lesson['frase']}\n\n"
            f"Si llegas al ejercicio 3 ya tienes el núcleo. Los siguientes y los auxiliares "
            f"consolidan.\n\n**Siguiente clase:** seguimos construyendo el motor sobre esta pieza."
            if nxt <= 15 else f"## Cierre\n\n{lesson['frase']}")


def emit(lesson: dict) -> None:
    folder = os.path.join(ROOT, lesson["slug"])
    pres = os.path.join(folder, "presentation")
    exer = os.path.join(folder, "exercises")
    os.makedirs(pres, exist_ok=True)
    os.makedirs(exer, exist_ok=True)
    os.makedirs(os.path.join(folder, "data"), exist_ok=True)

    has_pkg = stage_package(lesson["n"], exer)

    # docs
    with open(os.path.join(folder, "README.md"), "w") as f:
        f.write(readme(lesson, has_pkg))
    with open(os.path.join(folder, "CLAUDE.md"), "w") as f:
        f.write(claude_md(lesson, has_pkg))

    # assets a medida (rescatados / hechos a mano) tienen prioridad sobre el template
    custom_dir = os.path.join(HERE, "custom")
    custom_html = os.path.join(custom_dir, f"{lesson['n']:02d}.html")
    custom_guion = os.path.join(custom_dir, f"{lesson['n']:02d}_guion.md")
    slugname = lesson["slug"].split("-", 1)[1]

    if os.path.exists(custom_guion):
        shutil.copy(custom_guion, os.path.join(pres, "guion.md"))
    else:
        with open(os.path.join(pres, "guion.md"), "w") as f:
            f.write(guion_md(lesson))

    if os.path.exists(custom_html):
        shutil.copy(custom_html, os.path.join(pres, f"{slugname}-interactive.html"))
    else:
        with open(os.path.join(pres, f"{slugname}-interactive.html"), "w") as f:
            f.write(nbgen.build_html(lesson))

    # notebooks
    intro = (f"# 🐍 Clase {lesson['n']} · {lesson['title']}\n\n"
             f"> {lesson['objective']}\n\n"
             f"**Hoy construyes:** {lesson['piece']}.")
    build_nb = nbgen.build_notebook(intro, tiers_md("build"), lesson["build"],
                                    closing_build(lesson))

    # .py consolidado: que el alumno vea código en un archivo, no solo en celdas
    if lesson.get("script"):
        sname = lesson["script_name"]
        with open(os.path.join(exer, sname), "w") as f:
            f.write(lesson["script"])
        build_nb["cells"] += [
            nbgen.md(
                "## 🚀 Llévatelo a un `.py`\n\n"
                "Un notebook va genial para explorar, pero el código de verdad vive en archivos "
                f"`.py` que se ejecutan enteros de una vez. Abre **`{sname}`**: es lo que acabas de "
                "construir, ordenado en funciones reutilizables.\n\n"
                "Ejecútalo desde una terminal:\n\n"
                f"```bash\npython {sname}\n```\n\n"
                "…o aquí mismo, en la siguiente celda:"),
            nbgen.code(f"!python {sname}"),
            nbgen.md("> En la **clase 3** esas funciones darán el salto a **clases** (POO): "
                     "el mismo código, mejor organizado."),
        ]
    nbgen.write_notebook(os.path.join(exer, f"{lesson['n']:02d}_build_exercises.ipynb"), build_nb)

    aux_intro = (f"# Clase {lesson['n']} — Auxiliares\n\nProfundización opcional sobre "
                 f"*{lesson['title']}*.")
    aux_nb = nbgen.build_notebook(aux_intro, tiers_md("aux"), lesson["aux"],
                                  "## Fin de los auxiliares\n\nVuelve al cuaderno principal cuando quieras.")
    nbgen.write_notebook(os.path.join(exer, f"{lesson['n']:02d}_auxiliary.ipynb"), aux_nb)


def clean_old_folders() -> None:
    import re
    keep = {l["slug"] for l in LESSONS}
    keep |= {"15-final-exam"}
    for d in os.listdir(ROOT):
        if re.match(r"^\d\d-", d) and d not in keep:
            shutil.rmtree(os.path.join(ROOT, d))
            print("  removed old:", d)


def main() -> None:
    print("== Autovalidación de ejercicios ==")
    failures = self_test()
    if failures:
        print(f"FALLAN {len(failures)} ejercicios:\n")
        for f in failures:
            print(f)
        sys.exit(1)
    total = sum(len(l["build"]) + len(l["aux"]) for l in LESSONS)
    print(f"OK — {total} ejercicios validados en {len(LESSONS)} lecciones.")

    if "--check-only" in sys.argv:
        return

    print("\n== Emisión de lecciones ==")
    for lesson in LESSONS:
        emit(lesson)
        print(f"  L{lesson['n']:>2}  {lesson['slug']}")
    if "--clean" in sys.argv:
        print("\n== Limpieza de carpetas antiguas ==")
        clean_old_folders()
    print("\nHecho.")


if __name__ == "__main__":
    main()
