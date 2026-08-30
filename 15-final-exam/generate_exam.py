"""generate_exam.py — práctica acumulativa pública del curso (Clase 15).

Formato: test de 40 min, 40 preguntas, 3 opciones (A/B/C).
Baremo: acierto +1, fallo -0.5, en blanco 0.
Cubre todo el curso: Python/OOP, framework exchange, microestructura, tipos de
orden y matching, ejecución VWAP, market making y Avellaneda-Stoikov.

Uso:  python generate_exam.py
Genera: `examen.html` como práctica autocorregible pública. No genera ni
pretende sustituir el examen oficial, cuyo banco debe permanecer privado.
"""

from __future__ import annotations

import html
import os

# El banco de preguntas vive en question_bank.py (fuente única de verdad).
# CANONICAL = 40 preguntas públicas de práctica -> examen.html reproducible.
from question_bank import (  # noqa: E402
    CANONICAL as QUESTIONS, EXAM_POOL, EXAM_TARGETS,
    CHECKPOINT, CHECKPOINT_TARGETS, sample_balanced)


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


def _shuffled(questions=None, opt_seed: int = 2026):
    """Baraja las opciones de cada pregunta (semilla fija: examen reproducible)."""
    if questions is None:
        questions = QUESTIONS
    rng = _random.Random(opt_seed)
    out = []
    for (q, a, b, c, correct, topic) in questions:
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
  .codebox{display:flex;gap:8px;align-items:center;margin-top:14px;flex-wrap:wrap}
  .codebox code{font-family:var(--mono);font-size:.9rem;background:var(--bg);
    border:1px solid var(--line);border-radius:8px;padding:8px 12px;color:var(--accent);
    user-select:all;word-break:break-all}
  .codebox button{font-family:var(--mono);font-size:.78rem;padding:7px 12px;cursor:pointer;
    border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--text)}
  .codehint{font-size:.76rem;color:var(--muted);margin-top:6px}
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

const EXID=window.EXAM_ID||'L15',SEED=window.EXAM_SEED||0,MIN=window.EXAM_MIN||40;

/* checksum: debe coincidir con el de verify_result.py (misma fórmula) */
function checksum(seed,right,wrong,blank,total){
  return String((right*7+wrong*13+blank*17+seed*3+total*5)%97).padStart(2,'0');
}

/* temporizador */
let left=MIN*60;
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
  const total=qs.length;
  const score=right-0.5*wrong;
  const nota=Math.max(0,score/total*10);
  const chk=checksum(SEED,right,wrong,blank,total);
  const code=['AT26',EXID,'S'+SEED,'R'+right,'W'+wrong,'B'+blank,
              'N'+nota.toFixed(2),chk].join('-');
  $('#grade-panel').classList.remove('hidden');
  $('#grade-res').innerHTML=
    '<div class="gr">aciertos: <b style="color:var(--bid)">'+right+'</b> · fallos: '+
    '<b style="color:var(--ask)">'+wrong+'</b> · en blanco: '+blank+'</div>'+
    '<div class="gr">puntuación: <b>'+score.toFixed(1)+'</b> / '+total+
    ' &nbsp;→&nbsp; nota: <b style="font-size:1.3em">'+nota.toFixed(2)+'</b> / 10</div>'+
    '<div class="gr" style="color:var(--muted);font-size:.8rem">'+
    Object.entries(byTopic).map(([t,x])=>t+' '+x.r+'/'+x.n).join(' · ')+'</div>'+
    '<div class="codebox"><code id="rescode">'+code+'</code>'+
    '<button id="copybtn">📋 copiar código</button></div>'+
    '<div class="codehint">Autoinforme de práctica: comprueba transcripción, no certifica autoría ni nota.</div>';
  const cb=$('#copybtn');
  cb.addEventListener('click',()=>{
    const t=$('#rescode').textContent;
    const done=()=>{cb.textContent='✓ copiado';setTimeout(()=>cb.textContent='📋 copiar código',1500);};
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(done,()=>{});
    }else{
      const r=document.createRange();r.selectNode($('#rescode'));
      const sel=window.getSelection();sel.removeAllRanges();sel.addRange(r);
      try{document.execCommand('copy');done();}catch(e){}
      sel.removeAllRanges();
    }
  });
  $('#grade-btn').disabled=true;$('#grade-btn').textContent='✓ corregido';
  $('#grade-panel').scrollIntoView({behavior:'smooth'});
}
$('#grade-btn').addEventListener('click',()=>{
  if(nAnswered()<qs.length&&!confirm('Tienes preguntas en blanco (0 puntos, no restan). ¿Corregir igualmente?'))return;
  grade();
});
})();
"""


def render_page(prepared, *, title, eyebrow, h1, lede, head_left, footer,
                exam_id, lesson, minutes, seed, grade_label) -> str:
    """Página interactiva genérica (examen o checkpoint). `prepared` es la
    salida de `_shuffled`: lista de (pregunta, opciones, idx_correcto, tema)."""
    qs_html = []
    for i, (q, opts, ok_idx, topic) in enumerate(prepared, 1):
        buttons = "\n".join(
            f'<button class="opt">{"ABC"[k]} · {_html.escape(t)}</button>'
            for k, t in enumerate(opts))
        qs_html.append(
            f'<div class="q" data-ok="{ok_idx}" data-topic="{topic}">'
            f'<div class="qt">{i}. {_html.escape(q)} <span class="topic">{topic}</span></div>'
            f'<div class="opts">{buttons}</div></div>')
    questions = "\n".join(qs_html)
    n = len(prepared)
    mm = f"{minutes:02d}:00"
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{_css()}
{_EXAM_CSS}
</style>
</head>
<body class="assessment-linear" data-lesson="{lesson:02d}" data-delivery="assessment-linear">
<div class="exam-head"><div class="wrap">
  <span class="t">{head_left}</span>
  <span class="t">respondidas <b id="prog">0 / {n}</b></span>
  <span class="t">⏱ <b id="timer">{mm}</b></span>
</div></div>

<header class="hero wrap" style="padding:44px 0 10px">
  <div class="eyebrow">{eyebrow}</div>
  <h1 style="font-size:clamp(1.8rem,4vw,2.6rem)">{h1}</h1>
  <p class="lede">{lede}</p>
</header>

<main class="wrap">
  <div class="quiz">{questions}</div>
  <div class="btnrow" style="margin:26px 0">
    <button class="btn" id="grade-btn" style="font-size:1rem;padding:12px 26px">{grade_label}</button>
  </div>
  <div id="grade-panel" class="hidden">
    <h3>Resultado</h3>
    <div id="grade-res"></div>
  </div>
</main>
<footer>{footer}</footer>
<script>window.EXAM_ID={exam_id!r};window.EXAM_SEED={seed};window.EXAM_MIN={minutes};</script>
<script>{_EXAM_JS}</script>
</body>
</html>
"""


def render_interactive(seed: int = 0) -> str:
    """Práctica L15. seed=0 -> 40 canónicas; seed>0 -> variante pública."""
    if seed == 0:
        prepared = _shuffled(QUESTIONS, opt_seed=2026)
    else:
        sampled = sample_balanced(EXAM_POOL, EXAM_TARGETS, seed)
        prepared = _shuffled(sampled, opt_seed=2026 + seed)
    tag = "práctica canónica" if seed == 0 else f"práctica variante s{seed}"
    return render_page(
        prepared,
        title="L15 · Práctica acumulativa — Algo Trading ICAI 2026",
        eyebrow=f"<b>Algo Trading · ICAI 2026</b> · L15 · {tag}",
        h1=f"{len(prepared)} preguntas · 40 minutos",
        lede='Baremo: acierto <b style="color:var(--bid)">+1</b> · fallo '
             '<b style="color:var(--ask)">−0.5</b> · en blanco 0. Pulsa una opción para '
             'marcarla; vuelve a pulsarla para dejarla en blanco. Al final (o cuando el '
             'reloj llegue a cero), <strong>Corregir</strong>. Banco público de práctica: '
             '<strong>no es el examen oficial</strong> y su resultado no acredita nota. '
             'El capstone de L14 es una entrega autónoma separada.',
        head_left="<b>Práctica L15 · NO OFICIAL</b> · Algo Trading ICAI 2026",
        footer="L15 · Práctica acumulativa pública — no usar como convocatoria oficial",
        exam_id="L15P", lesson=15, minutes=40, seed=seed,
        grade_label="Corregir práctica")


def render_checkpoint(seed: int = 0) -> str:
    """Checkpoint de mitad de curso (tras L6): 20 preguntas de L1-L6, 20 min."""
    sampled = sample_balanced(CHECKPOINT, CHECKPOINT_TARGETS, seed)
    prepared = _shuffled(sampled, opt_seed=606 + seed)
    return render_page(
        prepared,
        title="Checkpoint L1-L6 — Algo Trading ICAI 2026",
        eyebrow="<b>Algo Trading · ICAI 2026</b> · checkpoint tras la clase 6",
        h1=f"{len(prepared)} preguntas · 20 minutos",
        lede=('Autoexamen de mitad de curso: Python, módulos y POO (clases 1-6). '
              'Mismo baremo que el final: acierto <b style="color:var(--bid)">+1</b> · '
              'fallo <b style="color:var(--ask)">−0.5</b> · en blanco 0. Si sacas un 6 '
              'o más, tienes la base para la segunda mitad (el motor).'),
        head_left="<b>Checkpoint L1-L6</b> · repaso de la base",
        footer="Checkpoint · la base de Python y POO antes de construir el motor",
        exam_id="CK6", lesson=6, minutes=20, seed=seed, grade_label="Corregir checkpoint")


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
    import argparse
    ap = argparse.ArgumentParser(description="Genera la práctica L15 y el checkpoint.")
    ap.add_argument("--seed", type=int, default=0,
                    help="0 = práctica canónica; N>0 = variante pública equilibrada.")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    assert len(QUESTIONS) == 40, f"el examen debe tener 40 preguntas, tiene {len(QUESTIONS)}"

    if args.seed == 0:
        # práctica pública + clave local de práctica + checkpoint
        with open(os.path.join(here, "examen.html"), "w") as f:
            f.write(render_interactive(0))
        with open(os.path.join(here, "examen_con_respuestas.html"), "w") as f:
            f.write(render_key())
        ck = os.path.abspath(os.path.join(here, "..", "06-oop-iii-inheritance", "checkpoint.html"))
        with open(ck, "w") as f:
            f.write(render_checkpoint(0))
        print(f"OK — práctica pública de {len(QUESTIONS)} preguntas. examen.html (+1/-0.5, 40:00), "
              f"examen_con_respuestas.html y checkpoint.html (L1-L6, 20:00) generados.")
    else:
        out = os.path.join(here, f"examen_s{args.seed}.html")
        with open(out, "w") as f:
            f.write(render_interactive(args.seed))
        print(f"OK — variante s{args.seed} equilibrada generada en {os.path.basename(out)} "
              f"(no versionada; solo práctica, nunca convocatoria oficial).")


if __name__ == "__main__":
    main()
