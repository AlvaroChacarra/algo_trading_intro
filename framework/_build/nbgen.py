"""nbgen.py — builders de notebooks y HTML para el curso.

El contenido de cada lección vive en specs (lessons_*.py). Este módulo los
convierte en .ipynb y en presentaciones HTML con el diseño compartido.

Cada ejercicio sigue el patrón probado en L1-L2:
    enunciado (md) -> starter (code) -> validador (code) -> solución (md)
Los validadores usan `assert` con mensajes claros.
"""

from __future__ import annotations

import json
import os

# ---------------------------------------------------------------------------
# Notebooks
# ---------------------------------------------------------------------------


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str, hidden: bool = False) -> dict:
    # hidden=True pliega el código fuente de la celda en Jupyter (source_hidden):
    # se ejecuta igual, pero aparece como una pestañita que se puede desplegar.
    meta = {"jupyter": {"source_hidden": True}} if hidden else {}
    return {"cell_type": "code", "metadata": meta, "execution_count": None,
            "outputs": [], "source": text.rstrip("\n").splitlines(keepends=True)}


def _exercise_cells(ex: dict) -> list[dict]:
    cells = []
    head = f"### {ex['title']}\n\n{ex['statement']}"
    if ex.get("hint"):
        head += f"\n\n> 💡 {ex['hint']}"
    head += f"\n\n<sub>practicas: {ex['practice']}</sub>"
    cells.append(md(head))

    starter = ex.get("given", "")
    if starter and not starter.endswith("\n"):
        starter += "\n"
    starter += ex.get("starter", "# Escribe aquí\n")
    cells.append(code(starter))
    # validador plegado (escondido pero ejecutable)
    cells.append(code("# ✅ Comprobación — ejecútala (Shift+Enter). Está plegada a propósito.\n"
                      + ex["validator"], hidden=True))
    # solución oculta tras una pestaña desplegable
    cells.append(md("<details>\n<summary>💡 Ver solución</summary>\n\n"
                    f"```python\n{ex['solution'].rstrip()}\n```\n\n</details>"))
    return cells


def build_notebook(intro_md: str, tiers_md: str | None, exercises: list[dict],
                   closing_md: str) -> dict:
    cells = [md(intro_md)]
    if tiers_md:
        cells.append(md(tiers_md))
    for ex in exercises:
        cells.extend(_exercise_cells(ex))
    cells.append(md(closing_md))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(path: str, nb: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# HTML (diseño compartido del curso)
# ---------------------------------------------------------------------------

_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>
  :root {{
    --bg:#09090b; --panel:#101014; --fg:#f4f4f5; --muted:#a1a1aa;
    --accent:#22d3ee; --green:#4ade80; --red:#f87171; --line:#27272a;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--fg); font-family:'Inter',sans-serif;
         scroll-snap-type:y mandatory; overflow-y:scroll; height:100vh; }}
  section {{ min-height:100vh; scroll-snap-align:start; display:flex; flex-direction:column;
            justify-content:center; padding:8vh 7vw; border-bottom:1px solid var(--line); }}
  .tag {{ color:var(--accent); font-weight:600; letter-spacing:.12em; text-transform:uppercase;
         font-size:.8rem; margin-bottom:1.2rem; }}
  h1 {{ font-size:clamp(2.2rem,6vw,4rem); font-weight:800; line-height:1.05; }}
  h2 {{ font-size:clamp(1.6rem,4vw,2.6rem); font-weight:800; margin-bottom:1.2rem; }}
  p {{ color:var(--muted); font-size:clamp(1rem,2vw,1.25rem); max-width:60ch; line-height:1.6;
      margin-top:1rem; }}
  .piece {{ display:inline-block; margin-top:2rem; padding:.5rem 1rem; border:1px solid var(--accent);
           border-radius:8px; color:var(--accent); font-family:'JetBrains Mono',monospace; font-size:.95rem; }}
  pre {{ margin-top:1.5rem; background:var(--panel); border:1px solid var(--line); border-radius:10px;
        padding:1.2rem 1.4rem; overflow-x:auto; font-family:'JetBrains Mono',monospace;
        font-size:.95rem; color:#e4e4e7; line-height:1.55; max-width:70ch; }}
  .k {{ color:var(--accent); }} .c {{ color:var(--muted); font-style:italic; }}
  .frase {{ font-size:clamp(1.3rem,3vw,2rem); color:var(--fg); font-weight:600; max-width:50ch; }}
  .dot {{ color:var(--accent); }}
  footer {{ color:var(--muted); font-size:.85rem; margin-top:3rem; font-family:'JetBrains Mono',monospace; }}
</style>
</head>
<body>
<section>
  <div class="tag">Clase {n} · {course}</div>
  <h1>{title}</h1>
  <p>{objective}</p>
  <span class="piece">Hoy construyes: {piece}</span>
</section>
{blocks}
<section>
  <div class="tag">Cierre</div>
  <p class="frase">{frase}</p>
  <footer>→ siguiente: abre <span class="k">exercises/</span> y construye la pieza.</footer>
</section>
<script>
  gsap.utils.toArray('section').forEach(s => {{
    gsap.from(s.children, {{ opacity:0, y:24, duration:.6, stagger:.08,
      scrollTrigger:{{ trigger:s, start:'top 70%' }} }});
  }});
  document.querySelectorAll('section').forEach(s =>
    gsap.from(s.children, {{opacity:0, y:20, duration:.5, stagger:.07,
      onStart(){{}}, scrollTrigger:undefined}}));
</script>
</body>
</html>"""

_BLOCK = """<section>
  <div class="tag">Bloque {i}</div>
  <h2>{heading}</h2>
  <p>{body}</p>
  {codehtml}
</section>"""


def _code_html(snippet: str | None) -> str:
    if not snippet:
        return ""
    import html
    esc = html.escape(snippet)
    return f"<pre>{esc}</pre>"


def build_html(lesson: dict, course: str = "Algo Trading · ICAI 2026") -> str:
    blocks = ""
    for i, blk in enumerate(lesson["concepts"], 1):
        heading, body, snippet = blk
        blocks += _BLOCK.format(i=i, heading=heading, body=body,
                                codehtml=_code_html(snippet))
    return _HTML.format(
        title=lesson["title"], n=lesson["n"], course=course,
        objective=lesson["objective"], piece=lesson["piece"],
        frase=lesson["frase"], blocks=blocks)
