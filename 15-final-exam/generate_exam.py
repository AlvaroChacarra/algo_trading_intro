"""generate_exam.py — examen final del curso (Clase 15).

Formato: test de 40 min, 40 preguntas, 3 opciones (A/B/C).
Baremo: acierto +1, fallo -0.5, en blanco 0.
Cubre todo el curso: Python/OOP, framework exchange, microestructura, tipos de
orden y matching, ejecución VWAP, market making y Avellaneda-Stoikov.

Uso:  python generate_exam.py
Genera:  examen.html  y  examen_con_respuestas.html
"""

from __future__ import annotations

import html
import os

# (pregunta, opción A, B, C, correcta, tema)
QUESTIONS = [
    # --- Python / OOP / framework -----------------------------------------
    ("En el framework, ¿qué hace que una estrategia sea 'enchufable' al Backtest sin tocar el runner?",
     "Que herede de Strategy e implemente on_book_update devolviendo acciones",
     "Que defina un método run() propio",
     "Que importe el módulo backtest",
     "A", "framework"),
    ("`Side(str, Enum)` se usa en vez de un str pelado porque…",
     "Es más rápido en tiempo de ejecución",
     "Evita valores inválidos como 'byu' pero sigue comparándose con 'buy'",
     "Permite ordenar las órdenes por precio",
     "B", "oop"),
    ("Una `Order` de tipo MARKET tiene `price = None`. ¿Por qué?",
     "Porque el precio se decide al cruzar contra el libro, no se fija de antemano",
     "Porque las market orders no se ejecutan nunca",
     "Por un bug heredado del dict original",
     "A", "oop"),
    ("`PositionTracker` guarda `_cash` y `_position` con guión bajo. Esa convención significa…",
     "Que son constantes y no cambian",
     "Que son estado interno: se modifican vía métodos, no a mano desde fuera",
     "Que Python las hace inaccesibles (privadas de verdad)",
     "B", "oop"),
    ("¿Qué devuelve `on_book_update`?",
     "Una lista de acciones (NewOrder/Cancel), no ejecuta nada por sí misma",
     "Los fills generados",
     "El nuevo equity",
     "A", "framework"),
    ("En el Backtest de replay, una LIMIT que no se cruza en un snapshot…",
     "Persiste para siempre en el libro",
     "Solo descansa dentro de ese snapshot; el libro se reconstruye en el siguiente paso",
     "Se convierte automáticamente en MARKET",
     "B", "framework"),
    ("`Fill.cash_flow()` de una compra de 0.5 @ 100 vale…",
     "+50",
     "-50",
     "0",
     "B", "oop"),
    ("La composición que ve el alumno en L4 es…",
     "OrderBook contiene niveles; PositionTracker consume objetos Fill",
     "Order hereda de OrderBook",
     "Market hereda de Strategy",
     "A", "oop"),
    ("¿Por qué `on_book_update` devuelve acciones en vez de ejecutar órdenes directamente?",
     "Para separar la decisión (estrategia) de la ejecución (motor)",
     "Porque ejecutar dentro sería más rápido",
     "Para evitar usar clases",
     "A", "framework"),
    ("Polimorfismo en el curso significa que…",
     "VWAP y un market maker se enchufan al mismo Backtest sin cambiar el runner",
     "Una orden puede ser buy y sell a la vez",
     "El libro cambia de tipo en tiempo de ejecución",
     "A", "framework"),

    # --- Microestructura ---------------------------------------------------
    ("El spread es…",
     "best_ask - best_bid",
     "best_bid - best_ask",
     "(best_bid + best_ask)/2",
     "A", "microstructure"),
    ("El microprice pondera el mid por…",
     "El tamaño del lado contrario (más peso al lado con menos tamaño)",
     "El número de niveles del libro",
     "La volatilidad histórica",
     "A", "microstructure"),
    ("Un imbalance de nivel 1 cercano a +1 indica…",
     "Mucho más tamaño en el bid que en el ask (presión compradora)",
     "Mucho más tamaño en el ask",
     "Spread muy ancho",
     "A", "microstructure"),
    ("La profundidad (depth) de un lado mide…",
     "El tamaño acumulado en los primeros niveles",
     "La distancia al mid",
     "El número de trades ejecutados",
     "A", "microstructure"),
    ("El mid simple frente al microprice…",
     "El microprice suele anticipar mejor el siguiente movimiento a corto plazo",
     "Son siempre idénticos",
     "El mid es mejor predictor a corto",
     "A", "microstructure"),
    ("Liquidez visible en el libro vs negociación real:",
     "El libro muestra intención; no todo se ejecuta y puede cancelarse",
     "Todo lo del libro se ejecuta seguro",
     "Son lo mismo",
     "A", "microstructure"),

    # --- Tipos de orden y matching ----------------------------------------
    ("Una MARKET buy de tamaño grande sobre un libro fino…",
     "Barre varios niveles y paga un precio efectivo peor que el best ask",
     "Se ejecuta toda al best ask",
     "Se cancela si no hay liquidez al best ask",
     "A", "matching"),
    ("Una orden IOC…",
     "Cruza lo que pueda y cancela el remanente (no descansa)",
     "Se ejecuta entera o nada",
     "Descansa en el libro indefinidamente",
     "A", "matching"),
    ("Una orden FOK…",
     "O se llena entera o no se ejecuta nada",
     "Llena parcialmente y deja el resto",
     "Siempre cruza al mid",
     "A", "matching"),
    ("Una LIMIT buy al best_bid actual (por debajo del ask)…",
     "No cruza: descansa en el libro",
     "Cruza contra el ask inmediatamente",
     "Se rechaza",
     "A", "matching"),
    ("El precio efectivo de una market que barre niveles es…",
     "El nocional total dividido por el tamaño total ejecutado",
     "Siempre el best bid",
     "El precio del último nivel tocado",
     "A", "matching"),
    ("Más tamaño en una market order implica, normalmente…",
     "Peor precio efectivo (más slippage)",
     "Mejor precio efectivo",
     "El mismo precio efectivo",
     "A", "matching"),
    ("La elección del tipo de orden afecta a…",
     "Coste, probabilidad de ejecución y riesgo",
     "Solo a la latencia",
     "Solo al símbolo",
     "A", "matching"),
    ("Cruzar ya (market) vs esperar barato (limit) es un trade-off entre…",
     "Certeza de ejecución vs precio",
     "Volatilidad vs volumen",
     "Cash vs equity",
     "A", "matching"),

    # --- Ejecución / VWAP --------------------------------------------------
    ("El objetivo de un algoritmo VWAP es…",
     "Ejecutar cerca del precio medio ponderado por volumen, troceando la orden",
     "Maximizar el número de fills",
     "Comprar al best bid siempre",
     "A", "execution"),
    ("TWAP frente a VWAP:",
     "TWAP reparte en trozos iguales en el tiempo; VWAP pondera por volumen",
     "TWAP pondera por volumen; VWAP por tiempo",
     "Son idénticos",
     "A", "execution"),
    ("Trocear una orden grande sirve para…",
     "Reducir el impacto de mercado (slippage)",
     "Aumentar el slippage a propósito",
     "Evitar pagar comisiones",
     "A", "execution"),
    ("La predicción dinámica de volumen (L11) usa…",
     "El flujo reciente (ventana rolada) además de la media histórica",
     "Solo la media de todos los días",
     "Únicamente el primer minuto",
     "A", "execution"),
    ("El factor de corrección de un schedule…",
     "Acelera si vas por detrás del plan y frena si vas por delante",
     "Siempre manda el mismo tamaño",
     "Cancela la orden si hay retraso",
     "A", "execution"),
    ("El benchmark natural de una ejecución es…",
     "El mid de llegada (arrival mid)",
     "El precio de cierre del año",
     "El best ask final",
     "A", "execution"),
    ("Un equity positivo con un inventario enorme al final indica…",
     "Riesgo escondido: no es necesariamente una buena estrategia",
     "Una estrategia perfecta",
     "Un error de cálculo seguro",
     "A", "execution"),

    # --- Market making / Avellaneda-Stoikov -------------------------------
    ("El PnL de un market maker viene de…",
     "Comprar en el bid y vender en el ask, capturando el spread",
     "Cruzar market orders agresivas",
     "Pagar el spread cada vuelta",
     "A", "mm"),
    ("El principal riesgo de un market maker es…",
     "El inventario (posición acumulada cuando el flujo es desequilibrado)",
     "Tener demasiada caja",
     "Cotizar un spread demasiado ancho",
     "A", "mm"),
    ("El skew por inventario consiste en…",
     "Bajar ambas cotizaciones cuando estás largo para volver a plano",
     "Subir el spread sin mover el centro",
     "Cancelar todas las órdenes",
     "A", "mm"),
    ("El reservation price de Avellaneda-Stoikov con inventario largo…",
     "Está por debajo del mid (incentiva soltar)",
     "Está por encima del mid",
     "Coincide siempre con el mid",
     "A", "as"),
    ("En r = s - q·γ·σ²·(T-t), al acercarse el cierre (t→T)…",
     "El ajuste por inventario tiende a 0 y r vuelve al mid",
     "El ajuste se hace máximo",
     "r se vuelve infinito",
     "A", "as"),
    ("Subir γ (aversión al riesgo) en A-S…",
     "Inclina más el reservation price y reduce el inventario acumulado",
     "Aumenta el inventario acumulado",
     "No tiene ningún efecto",
     "A", "as"),
    ("La utilidad CARA -exp(-γ·W)…",
     "Es creciente en riqueza y más cóncava cuanto mayor es γ",
     "Es decreciente en riqueza",
     "Es lineal en riqueza",
     "A", "as"),
    ("Adverse selection para un market maker significa…",
     "Acumular posición justo cuando el mercado se mueve en tu contra",
     "Cotizar el mismo precio que el competidor",
     "Tener un spread negativo",
     "A", "mm"),
    ("¿Por qué el market making se simula con un modelo de intensidad de fills λ(δ)=A·e^(-κδ)?",
     "Porque una limit lejos del mid se ejecuta con menos probabilidad que una cerca",
     "Porque las market orders siempre fallan",
     "Porque el mid nunca se mueve",
     "A", "as"),
]


PAGE = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
 body{{font-family:'Inter',system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1.2rem;color:#18181b;line-height:1.5}}
 h1{{font-size:1.6rem}} .meta{{background:#f4f4f5;border:1px solid #e4e4e7;border-radius:8px;padding:1rem 1.2rem;margin:1rem 0}}
 .q{{margin:1.1rem 0;padding:.8rem 1rem;border:1px solid #e4e4e7;border-radius:8px}}
 .qn{{font-weight:700}} .topic{{color:#71717a;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}}
 ol{{list-style:none;padding-left:0;margin:.5rem 0 0}} li{{margin:.25rem 0}}
 .opt{{font-weight:600;color:#0e7490;margin-right:.4rem}}
 .correct{{background:#dcfce7;border-color:#86efac}} .ans{{color:#15803d;font-weight:700}}
 @media print{{.q{{break-inside:avoid}}}}
</style></head><body>
<h1>{title}</h1>
<div class="meta">
 <b>Examen final — Introducción al Algo Trading con Python (ICAI 2026)</b><br>
 Duración: 40 minutos · 40 preguntas · 3 opciones (A/B/C).<br>
 <b>Baremo:</b> acierto <b>+1</b>, fallo <b>−0.5</b>, en blanco <b>0</b>.
</div>
{body}
</body></html>"""


# ---------------------------------------------------------------------------
# Emisión: examen interactivo (formato documento del curso)
# ---------------------------------------------------------------------------

import html as _html
import random as _random

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_HERE, "..", "framework", "_build", "doc_assets")


def _css() -> str:
    parts = []
    for f in ("fonts_embed.css", "shared.css", "extra.css"):
        p = os.path.join(_ASSETS, f)
        if os.path.exists(p):
            with open(p) as fh:
                parts.append(fh.read())
    return "\n".join(parts)


def _shuffled():
    """Baraja las opciones de cada pregunta (semilla fija: examen reproducible)."""
    rng = _random.Random(2026)
    out = []
    for (q, a, b, c, correct, topic) in QUESTIONS:
        opts = [a, b, c]
        correct_text = {"A": a, "B": b, "C": c}[correct]
        rng.shuffle(opts)
        out.append((q, opts, opts.index(correct_text), topic))
    return out


_EXAM_CSS = """
  .exam-head{position:sticky;top:0;z-index:30;background:rgba(9,9,11,.94);
    backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:12px 0}
  .exam-head .wrap{display:flex;justify-content:space-between;align-items:center;gap:16px}
  .exam-head .t{font-family:var(--mono);font-size:.8rem;color:var(--muted)}
  .exam-head b{color:var(--accent)}
  #timer.low{color:var(--ask)}
  .q .topic{font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;color:var(--faint);
    border:1px solid var(--line);border-radius:99px;padding:1px 8px;margin-left:8px;
    text-transform:uppercase;font-weight:400}
  .q .opt.sel{border-color:var(--accent);color:var(--accent)}
  #grade-panel{border:1px solid rgba(34,211,238,.4);border-radius:14px;padding:22px 26px;
    margin:30px 0;background:var(--accent-dim)}
  #grade-panel h3{margin:0 0 8px}
  .gr{font-family:var(--mono);font-size:.9rem;line-height:2}
"""

_EXAM_JS = """
(function(){
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const qs=$$('.q');let graded=false;

function nAnswered(){return qs.filter(q=>q.querySelector('.opt.sel')).length;}
function refresh(){$('#prog').textContent=nAnswered()+' / '+qs.length;}

qs.forEach(q=>{
  const opts=[...q.querySelectorAll('.opt')];
  opts.forEach(o=>o.addEventListener('click',()=>{
    if(graded)return;
    const was=o.classList.contains('sel');
    opts.forEach(x=>x.classList.remove('sel'));
    if(!was)o.classList.add('sel');   // volver a pulsar = dejar en blanco
    refresh();
  }));
});
refresh();

/* temporizador 40:00 */
let left=40*60;
const ti=setInterval(()=>{
  left--;
  const m=String(Math.floor(left/60)).padStart(2,'0'),s=String(left%60).padStart(2,'0');
  $('#timer').textContent=m+':'+s;
  if(left<=300)$('#timer').classList.add('low');
  if(left<=0){clearInterval(ti);grade();}
},1000);

function grade(){
  if(graded)return;graded=true;clearInterval(ti);
  let right=0,wrong=0,blank=0;
  const byTopic={};
  qs.forEach(q=>{
    const ok=+q.dataset.ok,topic=q.dataset.topic;
    const opts=[...q.querySelectorAll('.opt')];
    const selIdx=opts.findIndex(o=>o.classList.contains('sel'));
    opts.forEach(o=>o.disabled=true);
    opts[ok].classList.add('ok');
    byTopic[topic]=byTopic[topic]||{r:0,n:0};byTopic[topic].n++;
    if(selIdx===-1){blank++;}
    else if(selIdx===ok){right++;byTopic[topic].r++;}
    else{wrong++;opts[selIdx].classList.add('bad');}
  });
  const score=right-0.5*wrong;
  const nota=Math.max(0,score/qs.length*10);
  $('#grade-panel').classList.remove('hidden');
  $('#grade-res').innerHTML=
    '<div class="gr">aciertos: <b style="color:var(--bid)">'+right+'</b> · fallos: '+
    '<b style="color:var(--ask)">'+wrong+'</b> · en blanco: '+blank+'</div>'+
    '<div class="gr">puntuación: <b>'+score.toFixed(1)+'</b> / '+qs.length+
    ' &nbsp;→&nbsp; nota: <b style="font-size:1.3em">'+nota.toFixed(2)+'</b> / 10</div>'+
    '<div class="gr" style="color:var(--muted);font-size:.8rem">'+
    Object.entries(byTopic).map(([t,x])=>t+' '+x.r+'/'+x.n).join(' · ')+'</div>';
  $('#grade-btn').disabled=true;$('#grade-btn').textContent='✓ corregido';
  $('#grade-panel').scrollIntoView({behavior:'smooth'});
}
$('#grade-btn').addEventListener('click',()=>{
  if(nAnswered()<qs.length&&!confirm('Tienes preguntas en blanco (0 puntos, no restan). ¿Corregir igualmente?'))return;
  grade();
});
})();
"""


def render_interactive() -> str:
    qs_html = []
    for i, (q, opts, ok_idx, topic) in enumerate(_shuffled(), 1):
        buttons = "\n".join(
            f'<button class="opt">{"ABC"[k]} · {_html.escape(t)}</button>'
            for k, t in enumerate(opts))
        qs_html.append(
            f'<div class="q" data-ok="{ok_idx}" data-topic="{topic}">'
            f'<div class="qt">{i}. {_html.escape(q)} <span class="topic">{topic}</span></div>'
            f'<div class="opts">{buttons}</div></div>')
    questions = "\n".join(qs_html)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>L15 · Examen final — Algo Trading ICAI 2026</title>
<style>
{_css()}
{_EXAM_CSS}
</style>
</head>
<body>
<div class="exam-head"><div class="wrap">
  <span class="t"><b>Examen final</b> · Algo Trading ICAI 2026</span>
  <span class="t">respondidas <b id="prog">0 / 40</b></span>
  <span class="t">⏱ <b id="timer">40:00</b></span>
</div></div>

<header class="hero wrap" style="padding:44px 0 10px">
  <div class="eyebrow"><b>Algo Trading · ICAI 2026</b> · L15 · examen final</div>
  <h1 style="font-size:clamp(1.8rem,4vw,2.6rem)">40 preguntas · 40 minutos</h1>
  <p class="lede">Baremo: acierto <b style="color:var(--bid)">+1</b> · fallo
  <b style="color:var(--ask)">−0.5</b> · en blanco 0. Pulsa una opción para marcarla;
  vuelve a pulsarla para dejarla en blanco. Al final (o cuando el reloj llegue a cero),
  <strong>Corregir</strong>.</p>
</header>

<main class="wrap">
  <div class="quiz">{questions}</div>
  <div class="btnrow" style="margin:26px 0">
    <button class="btn" id="grade-btn" style="font-size:1rem;padding:12px 26px">Corregir examen</button>
  </div>
  <div id="grade-panel" class="hidden">
    <h3>Resultado</h3>
    <div id="grade-res"></div>
  </div>
</main>
<footer>L15 · Examen final — el curso entero, preguntado</footer>
<script>{_EXAM_JS}</script>
</body>
</html>
"""


def render_key() -> str:
    """Hoja de respuestas del profesor (orden barajado incluido)."""
    rows = []
    for i, (q, opts, ok_idx, topic) in enumerate(_shuffled(), 1):
        rows.append(f"<tr><td>{i}</td><td><b>{'ABC'[ok_idx]}</b></td>"
                    f"<td>{topic}</td><td>{_html.escape(q)}</td></tr>")
    body = "\n".join(rows)
    return ("<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            "<title>Examen — hoja de respuestas</title><style>"
            "body{font-family:system-ui;background:#09090b;color:#e6e6ea;padding:40px}"
            "table{border-collapse:collapse;font-size:14px}"
            "td{border:1px solid #26262c;padding:6px 12px}"
            "b{color:#22d3ee}</style></head><body>"
            "<h1>Hoja de respuestas (con opciones barajadas)</h1>"
            f"<table>{body}</table></body></html>")


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    assert len(QUESTIONS) == 40, f"el examen debe tener 40 preguntas, tiene {len(QUESTIONS)}"
    with open(os.path.join(here, "examen.html"), "w") as f:
        f.write(render_interactive())
    with open(os.path.join(here, "examen_con_respuestas.html"), "w") as f:
        f.write(render_key())
    print(f"OK — {len(QUESTIONS)} preguntas. Generados examen.html (interactivo, "
          f"+1/-0.5, 40:00) y examen_con_respuestas.html (hoja del profesor)")


if __name__ == "__main__":
    main()
