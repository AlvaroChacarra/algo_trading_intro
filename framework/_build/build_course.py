"""build_course.py — genera las lecciones L1-L14 desde los specs.

1. Autovalida cada ejercicio: exec(given + solution + validator) con el paquete
   de referencia en el path. Si algo falla, NO emite nada.
2. Emite por lección: README, CLAUDE, presentation/(html+guion),
   exercises/(build nb + aux nb + paquete exchange acumulado), data/.

Uso:  python build_course.py [--check-only]
"""

from __future__ import annotations

import os
import json
import shutil
import sys
import tempfile
import traceback

HERE = os.path.dirname(__file__)
FRAMEWORK = os.path.dirname(HERE)            # .../framework
ROOT = os.path.dirname(FRAMEWORK)            # .../algo_trading_intro
sys.path.insert(0, FRAMEWORK)               # para importar 'exchange'
sys.path.insert(0, HERE)

import docgen  # noqa: E402
import nbgen  # noqa: E402
from lessons_foundations import LESSONS as L_FOUND  # noqa: E402
from lessons_engine import LESSONS as L_ENG  # noqa: E402
from lessons_strategies import LESSONS as L_STRAT  # noqa: E402
from lessons_docs import DOCS as _RAW_DOCS, EXTRA_DOCS  # noqa: E402
from lessons_scripts import EXTRA_SCRIPTS  # noqa: E402

# Los DOCS se escribieron con la numeración previa (4 fundamentos). Tras pasar a
# 6 fundamentos, se remapean a la `n` actual; old 11 (VWAP II) y old 14 (A-S II)
# se funden en 12 y 14, así que se descartan.
_DOCS_REMAP = {1: 1, 2: 2, 3: 4, 4: 5, 5: 7, 6: 8, 7: 9, 8: 10, 9: 11, 10: 12, 12: 13, 13: 14}
DOCS = {_DOCS_REMAP[k]: v for k, v in _RAW_DOCS.items() if k in _DOCS_REMAP}
DOCS.update(EXTRA_DOCS)  # textos de las clases nuevas (L3 módulos, L6 herencia)

LESSONS = L_FOUND + L_ENG + L_STRAT
EXCHANGE_SRC = os.path.join(FRAMEWORK, "exchange")
EXERCISE_ROUTES_PATH = os.path.join(ROOT, "pedagogy", "exercise_routes.yml")
with open(EXERCISE_ROUTES_PATH, encoding="utf-8") as _fh:
    EXERCISE_ROUTES = json.load(_fh)["lessons"]


# ---------------------------------------------------------------------------
# 1) Autovalidación
# ---------------------------------------------------------------------------

def self_test() -> list[str]:
    failures = []
    for lesson in LESSONS:
        for kind in ("build", "aux"):
            try:
                assign_tiers(lesson[kind], kind, lesson["n"])
            except ValueError as exc:
                failures.append(str(exc))
        # Algunos ejercicios prueban imports y ejecución directa de los archivos
        # auxiliares reales de la lección. Los validamos en un workspace aislado
        # para que el check no dependa de una generación anterior ni ensucie el repo.
        with tempfile.TemporaryDirectory(prefix=f"lesson-{lesson['n']:02d}-") as workdir:
            for relpath, content in lesson.get("extra_files", {}).items():
                target = os.path.join(workdir, relpath)
                os.makedirs(os.path.dirname(target) or workdir, exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)

            old_cwd = os.getcwd()
            sys.path.insert(0, workdir)
            os.chdir(workdir)
            try:
                for kind in ("build", "aux"):
                    for ex in lesson.get(kind, []):
                        if "section" in ex:  # separador de bloque, no es un ejercicio
                            continue
                        ns: dict = {}
                        code = (ex.get("given", "") + "\n" + ex["solution"]
                                + "\n" + ex["validator"])
                        try:
                            exec(compile(code, f"L{lesson['n']}:{ex['title']}", "exec"), ns)
                        except Exception:
                            failures.append(
                                f"L{lesson['n']} [{kind}] {ex['title']}\n"
                                + traceback.format_exc())
            finally:
                os.chdir(old_cwd)
                sys.path.remove(workdir)
    return failures


# ---------------------------------------------------------------------------
# 2) Staging del paquete acumulado
# ---------------------------------------------------------------------------

def modules_for(n: int):
    core, strat, top = [], [], []
    if n >= 4:
        core += ["orders.py", "trades.py"]
        top += [("orders", "Order, Side, OrderType"), ("trades", "Fill")]
    if n >= 5:
        core += ["book.py", "portfolio.py"]
        top += [("book", "OrderBook, Level"), ("portfolio", "PositionTracker")]
    if n >= 8:
        core += ["matching.py"]
        top += [("matching", "MatchingEngine")]
    if n >= 9:
        core += ["market.py"]
        top += [("market", "Market")]
    if n >= 10:
        core += ["strategy.py", "backtest.py"]
        top += [("strategy", "Strategy, NewOrder, Cancel, Action"),
                ("backtest", "Backtest, BacktestResult")]
    if n >= 12:
        strat += [("vwap", "VWAPStrategy")]
    if n >= 13:
        strat += [("market_maker", "MarketMaker, AvellanedaStoikov")]
        core += ["simulation.py"]
    return core, strat, top


def stage_package(n: int, dest_exercises: str) -> bool:
    core, strat, top = modules_for(n)
    if not (core or strat):
        return False
    pkg = os.path.join(dest_exercises, "exchange")
    # El paquete es un output generado acumulativo: reconstruirlo evita que una
    # pieza de una lesson posterior sobreviva como archivo obsoleto al regenerar.
    if os.path.isdir(pkg):
        shutil.rmtree(pkg)
    os.makedirs(pkg, exist_ok=True)

    for f in core:
        shutil.copy(os.path.join(EXCHANGE_SRC, f), os.path.join(pkg, f))
    if n >= 7:  # datos para Market.sample()
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

def tiers_md(kind: str, explicit_routes: bool = False) -> str:
    if explicit_routes:
        intro = ("### Cómo funciona este cuaderno\n\n" if kind == "build" else
                 "### El gimnasio\n\n")
        return (intro
                + "Cada ejercicio declara una ruta pedagógica, decidida por contenido y no por posición: "
                "**🟢 LIVE** (núcleo presencial) · **🔵 REQUIRED** (consolidación autónoma "
                "requerida y evaluable) · **🟣 OPTIONAL** (profundización no obligatoria y no "
                "evaluable). Escribe tu respuesta, ejecuta la **✅ comprobación plegada** con "
                "`Shift+Enter` y usa la pista o solución solo cuando la necesites.")
    if kind == "build":
        return ("### Cómo funciona este cuaderno\n\n"
                "1. Escribe tu respuesta en la celda de código.\n"
                "2. Debajo hay una **✅ comprobación plegada**: ejecútala con `Shift+Enter` para validarte "
                "(despliégala si quieres ver el `assert`).\n"
                "3. ¿Atascado? Algunos ejercicios traen una **💭 Pista** intermedia; si no basta, "
                "abre **💡 Ver solución**.\n\n"
                "Cada ejercicio lleva su etiqueta: **🟢 núcleo** (en clase) · **🔵 si vamos bien** · "
                "**🟣 bonus** (el cuaderno de auxiliares profundiza más).")
    return ("### El gimnasio\n\n"
            "Drills cortos para automatizar las primitivas de Python con datos de mercado, "
            "más una profundización final. Mismo formato de siempre: escribe tu código, ejecuta la "
            "**✅ comprobación plegada** (`Shift+Enter`) y, si te atascas, abre **💡 Ver solución**. "
            "Ninguno debería llevarte más de un par de minutos. No hacen falta para seguir el "
            "curso — pero te hacen rápido.\n\n"
            "**Dosis mínima** = todo lo marcado **🟢 núcleo**: el calentamiento entero y los dos "
            "primeros drills de cada bloque. Lo **🔵 si vamos bien** y lo **🟣 bonus**, para volver otro día.")


def assign_tiers(exercises: list[dict], kind: str, lesson_n: int | None = None) -> None:
    """Rellena tier/min donde el spec no los fija, siguiendo la política declarada.

    build:  los 3 primeros = núcleo, el resto = si vamos bien.
    aux:    calentamiento entero + 2 primeros drills de cada bloque = núcleo
            (la "dosis mínima"), el resto del bloque = si vamos bien,
            y las secciones de profundización/curiosos/transferencia = bonus.
    Un `tier`/`min` explícito en el spec siempre gana.
    """
    explicit = EXERCISE_ROUTES.get(str(lesson_n), {}).get(kind) if lesson_n else None
    if explicit is not None:
        declared = {item["title"]: item for item in explicit}
        actual = [ex["title"] for ex in exercises if "section" not in ex]
        if set(actual) != set(declared) or len(actual) != len(declared):
            missing = sorted(set(actual) - set(declared))
            stale = sorted(set(declared) - set(actual))
            raise ValueError(
                f"L{lesson_n} {kind}: exercise route contract mismatch; "
                f"missing={missing}, stale={stale}"
            )
        for ex in exercises:
            if "section" in ex:
                continue
            decision = declared[ex["title"]]
            if decision["route"] not in {"LIVE", "REQUIRED", "OPTIONAL"}:
                raise ValueError(
                    f"L{lesson_n} {kind}: invalid route {decision['route']} for {ex['title']}"
                )
            ex["route"] = decision["route"]
            ex["min"] = decision["minutes"]
        return

    if kind == "build":
        i = 0
        for ex in exercises:
            if "section" in ex:
                continue
            i += 1
            ex.setdefault("tier", "nucleo" if i <= 3 else "bien")
            ex.setdefault("min", 5 if ex["tier"] == "nucleo" else 6)
        return

    mode, pos = "bloque", 0
    for ex in exercises:
        if "section" in ex:
            t = ex["section"].lower()
            if "calentamiento" in t:
                mode = "calentamiento"
            elif any(k in t for k in ("para curiosos", "para terminar", "transferencia")):
                mode = "bonus"
            else:
                mode = "bloque"
            pos = 0
            continue
        pos += 1
        if mode == "calentamiento":
            ex.setdefault("tier", "nucleo")
            ex.setdefault("min", 1)
        elif mode == "bonus":
            ex.setdefault("tier", "bonus")
            ex.setdefault("min", 5)
        else:
            ex.setdefault("tier", "nucleo" if pos <= 2 else "bien")
            ex.setdefault("min", 2)


def time_totals_md(exercises: list[dict]) -> str:
    if any(ex.get("route") for ex in exercises if "section" not in ex):
        totals = {"LIVE": 0, "REQUIRED": 0, "OPTIONAL": 0}
        for ex in exercises:
            if "section" not in ex:
                totals[ex["route"]] += ex.get("min", 0)
        parts = [f"🟢 LIVE ~{totals['LIVE']} min"]
        if totals["REQUIRED"]:
            parts.append(f"🔵 REQUIRED +{totals['REQUIRED']} min")
        if totals["OPTIONAL"]:
            parts.append(f"🟣 OPTIONAL +{totals['OPTIONAL']} min")
        return "⏱️ " + " · ".join(parts) + "."
    tot = {"nucleo": 0, "bien": 0, "bonus": 0}
    for ex in exercises:
        if "section" not in ex:
            tot[ex.get("tier", "bien")] += ex.get("min", 0)
    parts = [f"🟢 núcleo ~{tot['nucleo']} min"]
    if tot["bien"]:
        parts.append(f"🔵 si vamos bien +{tot['bien']} min")
    if tot["bonus"]:
        parts.append(f"🟣 bonus +{tot['bonus']} min")
    return "⏱️ " + " · ".join(parts) + "."


def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text)


def readme(lesson: dict, has_pkg: bool) -> str:
    doc = DOCS.get(lesson["n"], {})
    pkg_line = ("- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)\n"
                if has_pkg else "")
    build = "\n".join(f"- **{ex['title']}** — {ex['practice']}" for ex in lesson["build"])
    route_note = ("rutas LIVE / REQUIRED / OPTIONAL declaradas"
                  if str(lesson["n"]) in EXERCISE_ROUTES else "núcleo 1-3, luego el resto")
    return (f"# Clase {lesson['n']} — {lesson['title']}\n\n"
            f"> {lesson['objective']}\n\n"
            f"## Contexto teórico\n\n{doc.get('theory', '')}\n\n"
            f"## Qué construyes hoy\n\n**{lesson['piece']}**\n\n"
            f"{doc.get('technical', '')}\n\n"
            f"## Ejercicios de construcción\n\n{build}\n\n"
            f"## Estructura de la carpeta\n\n"
            f"- `presentation/` — documento interactivo (o deck) + guion del profesor\n"
            f"- `exercises/{lesson['n']:02d}_build_exercises.ipynb` — construyes la pieza ({route_note})\n"
            f"- `exercises/{lesson['n']:02d}_auxiliary.ipynb` — el gimnasio: drills + profundización opcional\n"
            f"{pkg_line}\n"
            f"## Idea central\n\n> {_strip_html(lesson['frase'])}\n")


def claude_md(lesson: dict, has_pkg: bool) -> str:
    doc = DOCS.get(lesson["n"], {})
    blocks = "\n".join(f"{i}. **{b[0]}** — {b[1]}" for i, b in enumerate(lesson["concepts"], 1))
    classification = (
        "Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en "
        "`pedagogy/exercise_routes.yml`. Auxiliares: "
        f"`{lesson['n']:02d}_auxiliary.ipynb`."
        if str(lesson["n"]) in EXERCISE_ROUTES else
        "Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, "
        f"**Auxiliares** = cuaderno `{lesson['n']:02d}_auxiliary.ipynb`."
    )
    return (f"# Clase {lesson['n']} — {lesson['title']} (guía de implementación)\n\n"
            f"Pieza del framework: **{lesson['piece']}**.\n\n"
            f"## Teoría que cubre\n\n{doc.get('theory', '')}\n\n"
            f"## Implementación técnica\n\n{doc.get('technical', '')}\n\n"
            f"## Presentación (3 bloques)\n\n{blocks}\n\n"
            f"## Cuaderno de construcción\n\n"
            f"Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con "
            f"mensaje claro, tolerancia `1e-9`) → solución guiada embebida.\n"
            f"{classification}\n\n"
            f"El contenido se genera desde `framework/_build/` — para editar esta clase, edita su "
            f"spec y regenera con `build_course.py`. No edites a mano los notebooks.\n\n"
            f"## Continuidad\n\n"
            f"{'El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.' if has_pkg else 'Aún sin paquete: el código se construye en celdas del notebook. El vocabulario de hoy se convierte en los atributos de las clases en L4.'}\n")


def guion_md(lesson: dict) -> str:
    slugname = lesson["slug"].split("-", 1)[1]
    out = [f"# Guion — Clase {lesson['n']}: {lesson['title']}\n",
           f"**Idea central:** {lesson['frase']}\n",
           f"**Formato:** documento interactivo (`{slugname}-doc.html`), autocontenido y sin "
           "internet. Tú haces scroll y narras. Regla de la casa: **\"lo cian se toca\"**.\n",
           "Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada "
           "es una idea) → simulador estrella (cede el teclado) → secciones de construcción "
           "(con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → "
           "mapa del paquete + puente.\n\n## Los bloques conceptuales\n"]
    for i, (h, body, _snip) in enumerate(lesson["concepts"], 1):
        out.append(f"\n### {i}. {h}\n")
        out.append(f"- **Qué decir:** {body}")
    out.append("\n## Cierre\n- Recoge la idea central sobre el mapa del paquete y manda al "
               "notebook de construcción; presenta el gimnasio (dosis mínima declarada).")
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

    if docgen.has_doc(lesson["n"]):
        # documento interactivo ("html corrido"): sustituye al deck en esta lección
        with open(os.path.join(pres, f"{slugname}-doc.html"), "w") as f:
            f.write(docgen.build_doc(lesson))
        old_deck = os.path.join(pres, f"{slugname}-interactive.html")
        if os.path.exists(old_deck):
            os.remove(old_deck)
    elif os.path.exists(custom_html):
        shutil.copy(custom_html, os.path.join(pres, f"{slugname}-interactive.html"))
    else:
        with open(os.path.join(pres, f"{slugname}-interactive.html"), "w") as f:
            f.write(nbgen.build_html(lesson))

    # notebooks
    explicit_routes = str(lesson["n"]) in EXERCISE_ROUTES
    assign_tiers(lesson["build"], "build", lesson["n"])
    assign_tiers(lesson["aux"], "aux", lesson["n"])
    intro = (f"# 🐍 Clase {lesson['n']} · {lesson['title']}\n\n"
             f"> {lesson['objective']}\n\n"
             f"**Hoy construyes:** {lesson['piece']}.\n\n"
             f"{time_totals_md(lesson['build'])}")
    build_nb = nbgen.build_notebook(intro, tiers_md("build", explicit_routes), lesson["build"],
                                    closing_build(lesson))

    # archivos extra (p.ej. un módulo que el alumno importa)
    for fname, content in lesson.get("extra_files", {}).items():
        with open(os.path.join(exer, fname), "w") as f:
            f.write(content)

    # capstone (L14): el proyecto abierto de cierre — plantilla + corrector + baremo
    capstone_src = os.path.join(HERE, "capstone")
    if lesson["n"] == 14 and os.path.isdir(capstone_src):
        shutil.copy(os.path.join(capstone_src, "CAPSTONE.md"),
                    os.path.join(folder, "CAPSTONE.md"))
        for fname in ("mi_estrategia.py", "capstone_check.py",
                      "capstone_scoring.py", "leaderboard.py"):
            shutil.copy(os.path.join(capstone_src, fname), os.path.join(exer, fname))

    # .py consolidado: que el alumno vea código en un archivo, no solo en celdas
    sname = lesson.get("script_name")
    script = lesson.get("script")
    if not script and lesson["n"] in EXTRA_SCRIPTS:
        sname, script = EXTRA_SCRIPTS[lesson["n"]]
    if script:
        with open(os.path.join(exer, sname), "w") as f:
            f.write(script)
        if lesson["n"] <= 3:
            bridge = ("> En la **clase 4** este código dará el salto a **clases** (POO): "
                      "el mismo código, mejor organizado.")
        else:
            bridge = ("> Es la misma pieza que vive en el paquete `exchange/` — aquí, "
                      "condensada en un archivo que puedes leer de una sentada.")
        build_nb["cells"] += [
            nbgen.md(
                "## 🚀 Llévatelo a un `.py`\n\n"
                "Un notebook va genial para explorar, pero el código de verdad vive en archivos "
                f"`.py` que se ejecutan enteros de una vez. Abre **`{sname}`**: es lo que acabas de "
                "construir, ordenado y de una pieza.\n\n"
                "Ejecútalo desde una terminal:\n\n"
                f"```bash\npython {sname}\n```\n\n"
                "…o aquí mismo, en la siguiente celda:"),
            nbgen.code(f"!python {sname}"),
            nbgen.md(bridge),
        ]
    nbgen.write_notebook(os.path.join(exer, f"{lesson['n']:02d}_build_exercises.ipynb"), build_nb)

    n_aux = sum(1 for ex in lesson["aux"] if "section" not in ex)
    aux_intro = (f"# Clase {lesson['n']} — Auxiliares · el gimnasio\n\n"
                 f"{n_aux} ejercicios cortos sobre *{lesson['title']}*: drills para ganar "
                 f"soltura con las primitivas y profundizaciones opcionales.\n\n"
                 f"{time_totals_md(lesson['aux'])}")
    aux_nb = nbgen.build_notebook(aux_intro, tiers_md("aux", explicit_routes), lesson["aux"],
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
    total = sum(1 for l in LESSONS for k in ("build", "aux")
                for ex in l[k] if "section" not in ex)
    print(f"OK — {total} ejercicios validados en {len(LESSONS)} lecciones.")

    if "--check-only" in sys.argv:
        return

    print("\n== Emisión de lecciones ==")
    for lesson in LESSONS:
        emit(lesson)
        print(f"  L{lesson['n']:>2}  {lesson['slug']}")
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(docgen.build_index(LESSONS, ROOT))
    print("  --  index.html (índice del curso)")
    if "--clean" in sys.argv:
        print("\n== Limpieza de carpetas antiguas ==")
        clean_old_folders()
    print("\nHecho.")


if __name__ == "__main__":
    main()
