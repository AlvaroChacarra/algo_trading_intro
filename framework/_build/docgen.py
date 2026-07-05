"""docgen.py — ensambla los documentos interactivos ("html corrido") de las lecciones.

Cada documento = base compartida + contenido a medida:
  doc_assets/fonts_embed.css   fuentes Inter + JetBrains Mono embebidas (offline)
  doc_assets/shared.css        sistema de diseño y componentes (extraído del doc de L1)
  doc_assets/extra.css         componentes añadidos después de L1 (pkgmap, cta, ...)
  docs/NN_body.html            el contenido de la lección (secciones)
  docs/NN_custom.js            los simuladores a medida de la lección

El JS compartido (SHARED_JS) implementa los motores genéricos, activados por
marcado, no por ids: raíl (#rail), botones ▶ (.runbtn[data-target]),
tracebacks (.tbBtn[data-tb]), quiz (.quiz[data-quiz]), scrollytelling
(.scrolly[data-scrolly]) y gates de predicción (.predictgate).
L1 conserva sus simuladores propios (sin data-attrs, no colisionan).
"""

from __future__ import annotations

import importlib.util
import json
import os

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "doc_assets")
DOCS = os.path.join(HERE, "docs")


def _doc_data(n: int) -> str:
    """Si existe docs/NN_data.py, ejecuta su build() con el motor exchange REAL
    y devuelve un <script> con los resultados. Así los simuladores del doc
    reproducen números calculados por el motor de referencia — nunca mienten."""
    path = os.path.join(DOCS, f"{n:02d}_data.py")
    if not os.path.exists(path):
        return ""
    spec = importlib.util.spec_from_file_location(f"doc{n:02d}_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    payload = json.dumps(mod.build(), separators=(",", ":"))
    return f"<script>const DOC_DATA={payload};</script>\n"


SHARED_JS = r"""
(function(){
"use strict";
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── mini-gráficas canvas (compartidas por los docs con datos reales) ── */
window.DOC=window.DOC||{};
DOC.chart=function(canvas,seriesList,opts={}){
  const c=typeof canvas==='string'?document.querySelector(canvas):canvas;
  const dpr=window.devicePixelRatio||1;
  const W=c.clientWidth||600,H=c.clientHeight||160;
  c.width=W*dpr;c.height=H*dpr;
  const ctx=c.getContext('2d');ctx.scale(dpr,dpr);ctx.clearRect(0,0,W,H);
  const all=seriesList.flatMap(s=>s.data.slice(0,s.upTo??s.data.length));
  if(!all.length)return;
  let lo=Math.min(...all),hi=Math.max(...all);
  if(opts.zero){lo=Math.min(lo,0);hi=Math.max(hi,0);}
  if(hi-lo<1e-9){hi=lo+1;}
  const pad=8,X=i=>pad+(W-2*pad)*i/(seriesList[0].data.length-1||1),
        Y=v=>H-pad-(H-2*pad)*(v-lo)/(hi-lo);
  ctx.strokeStyle='#26262c';ctx.lineWidth=1;
  if(lo<0&&hi>0){ctx.beginPath();ctx.moveTo(pad,Y(0));ctx.lineTo(W-pad,Y(0));ctx.stroke();}
  seriesList.forEach(s=>{
    const n=s.upTo??s.data.length;
    ctx.strokeStyle=s.color||'#22d3ee';ctx.lineWidth=s.width||1.6;
    ctx.beginPath();
    for(let i=0;i<n;i++){const x=X(i),y=Y(s.data[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}
    ctx.stroke();
    if(s.endDot&&n>0){ctx.fillStyle=s.color||'#22d3ee';
      ctx.beginPath();ctx.arc(X(n-1),Y(s.data[n-1]),3,0,7);ctx.fill();}
  });
  (opts.marks||[]).forEach(m=>{ctx.fillStyle=m.color||'#fbbf24';
    ctx.beginPath();ctx.arc(X(m.i),Y(m.v),3.4,0,7);ctx.fill();});
};

/* ── raíl de progreso ── */
(function(){
  const links=$$('#rail a');
  if(!links.length)return;
  const map={};links.forEach(a=>map[a.getAttribute('href').slice(1)]=a);
  const io=new IntersectionObserver(es=>{
    es.forEach(e=>{if(e.isIntersecting){
      links.forEach(a=>a.classList.remove('on'));
      (map[e.target.id]||links[0]).classList.add('on');
    }});
  },{rootMargin:'-35% 0px -55% 0px'});
  $$('header[id],section[id]').forEach(s=>io.observe(s));
})();

/* ── gates de predicción: el ▶ se desbloquea al escribir ── */
$$('.predictgate').forEach(g=>{
  const i=g.querySelector('input'),b=g.querySelector('.runbtn');
  if(!i||!b)return;
  b.disabled=true;
  i.addEventListener('input',()=>{b.disabled=i.value.trim()==='';});
});

/* ── botones ▶ genéricos: revelan su data-target ── */
$$('.runbtn[data-target]').forEach(b=>b.addEventListener('click',()=>{
  const t=document.getElementById(b.dataset.target);
  if(t){
    t.classList.remove('hidden');
    if(b.dataset.seq!==undefined){
      const rows=[...t.children];
      rows.forEach((r,k)=>{r.style.opacity=0;
        setTimeout(()=>{r.style.transition='opacity .4s';r.style.opacity=1;},reduced?0:280*(k+1));});
    }
  }
  const inp=b.closest('.predictgate')&&b.closest('.predictgate').querySelector('input');
  if(inp)inp.disabled=true;
  b.disabled=true;b.textContent=b.dataset.done||'✓ ejecutado';
}));

/* ── tarjetas de traceback ── */
$$('.tbBtn').forEach(b=>b.addEventListener('click',()=>{
  const tb=document.getElementById(b.dataset.tb);
  if(tb)tb.classList.remove('hidden');
  const notes=document.querySelector(`[data-for="${b.dataset.tb}"]`);
  if(notes)notes.classList.remove('hidden');
  b.disabled=true;b.textContent='💥 ejecutado';
}));

/* ── quiz genérico ── */
$$('.quiz[data-quiz]').forEach(qz=>{
  let answered=0,right=0;
  const qs=[...qz.querySelectorAll('.q')],score=qz.querySelector('.score');
  qs.forEach(q=>{
    const ok=+q.dataset.ok,opts=[...q.querySelectorAll('.opt')];
    opts.forEach((o,idx)=>o.addEventListener('click',()=>{
      opts.forEach(x=>x.disabled=true);
      opts[ok].classList.add('ok');
      if(idx!==ok)o.classList.add('bad');else right++;
      const w=q.querySelector('.why');if(w)w.classList.add('show');
      answered++;
      if(answered===qs.length){
        if(score)score.textContent=
          `Resultado: ${right}/${qs.length}`+(right===qs.length?' — impecable.'
            :right>=Math.ceil(qs.length*0.6)?' — sólido; revisa las que fallaste.'
            :' — relee las secciones marcadas y reintenta.');
        DOC.save({quiz:{right,total:qs.length,ts:Date.now()}});
      }
    }));
  });
});

/* ── progreso persistente (localStorage) ── */
DOC.key=()=> 'algoTrading.'+(document.body.dataset.lesson||'x');
DOC.save=function(patch){
  try{
    const k=DOC.key(),cur=JSON.parse(localStorage.getItem(k)||'{}');
    Object.assign(cur,patch);
    localStorage.setItem(k,JSON.stringify(cur));
  }catch(_){/* modo incógnito, etc. */}
};
(function(){
  if(!document.body.dataset.lesson)return;
  let maxPct=0,dirty=false;
  try{maxPct=(JSON.parse(localStorage.getItem(DOC.key())||'{}').scroll)||0;}catch(_){}
  addEventListener('scroll',()=>{
    const h=document.documentElement.scrollHeight-innerHeight;
    if(h<=0)return;
    const pct=Math.round(100*scrollY/h);
    if(pct>maxPct){maxPct=pct;dirty=true;}
  },{passive:true});
  setInterval(()=>{if(dirty){DOC.save({scroll:maxPct});dirty=false;}},2000);
  addEventListener('beforeunload',()=>{if(dirty)DOC.save({scroll:maxPct});});
})();

/* ── navegación por teclado en el scrolly (para proyectar) ── */
(function(){
  const steps=$$('.scrolly .step');
  if(!steps.length)return;
  document.addEventListener('keydown',e=>{
    if(!['ArrowDown','ArrowUp','PageDown','PageUp'].includes(e.key))return;
    if(/INPUT|TEXTAREA|SELECT|BUTTON/.test(document.activeElement.tagName))return;
    const mid=innerHeight/2;
    let idx=0,best=1e12;
    steps.forEach((s,i)=>{const r=s.getBoundingClientRect();
      const d=Math.abs(r.top+r.height/2-mid);if(d<best){best=d;idx=i;}});
    const r=steps[idx].getBoundingClientRect();
    if(r.bottom<-innerHeight*1.5||r.top>innerHeight*2.5)return; // lejos: scroll normal
    e.preventDefault();
    const fwd=(e.key==='ArrowDown'||e.key==='PageDown');
    const next=fwd?Math.min(idx+1,steps.length-1):Math.max(idx-1,0);
    steps[next].scrollIntoView({behavior:reduced?'auto':'smooth',block:'center'});
  });
})();

/* ── modo profesor: ?profe=1 abre el guion como cajón lateral ── */
(function(){
  const srcEl=document.getElementById('guion-src');
  if(!srcEl||!new URLSearchParams(location.search).has('profe'))return;
  const mdlite=t=>t
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/^### (.*)$/gm,'<h4>$1</h4>')
    .replace(/^## (.*)$/gm,'<h3>$1</h3>')
    .replace(/^# (.*)$/gm,'<h2>$1</h2>')
    .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/^- (.*)$/gm,'<li>$1</li>')
    .replace(/^---$/gm,'<hr>')
    .replace(/\n{2,}/g,'</p><p>');
  const drawer=document.createElement('aside');
  drawer.id='guion-drawer';
  drawer.innerHTML='<div class="gd-head">📋 Guion del profesor'
    +'<button id="gd-close" aria-label="Cerrar">✕</button></div>'
    +'<div class="gd-body"><p>'+mdlite(srcEl.textContent)+'</p></div>';
  document.body.appendChild(drawer);
  const btn=document.createElement('button');
  btn.id='gd-toggle';btn.className='btn';btn.textContent='📋 Guion';
  document.body.appendChild(btn);
  const toggle=()=>drawer.classList.toggle('open');
  btn.addEventListener('click',toggle);
  drawer.querySelector('#gd-close').addEventListener('click',toggle);
})();

/* ── scrollytelling genérico ──
   El paso activo enciende la .fig-stage del mismo número y avisa a la fig
   con un CustomEvent('stagechange') por si la lección quiere animar algo. */
$$('.scrolly[data-scrolly]').forEach(sc=>{
  const steps=[...sc.querySelectorAll('.step')],fig=sc.querySelector('.fig'),
        stages=[...sc.querySelectorAll('.fig-stage')],nameEl=sc.querySelector('.stage-name');
  const io=new IntersectionObserver(es=>{
    es.forEach(e=>{if(e.isIntersecting){
      const st=+e.target.dataset.stage;
      steps.forEach(x=>x.classList.toggle('on',x===e.target));
      stages.forEach(s=>s.classList.toggle('on',+s.dataset.stage===st));
      if(nameEl&&e.target.dataset.name)nameEl.textContent=e.target.dataset.name;
      if(fig)fig.dispatchEvent(new CustomEvent('stagechange',{detail:{stage:st}}));
    }});
  },{rootMargin:'-42% 0px -42% 0px'});
  steps.forEach(s=>io.observe(s));
});
})();
"""


def _css() -> str:
    return (open(os.path.join(ASSETS, "fonts_embed.css")).read()
            + open(os.path.join(ASSETS, "shared.css")).read()
            + open(os.path.join(ASSETS, "extra.css")).read())


def _guion_embed(n: int) -> str:
    """Guion del profesor embebido (visible solo con ?profe=1)."""
    path = os.path.join(HERE, "custom", f"{n:02d}_guion.md")
    if not os.path.exists(path):
        return ""
    text = open(path).read().replace("</script", "<\\/script")
    return f'<script type="text/plain" id="guion-src">{text}</script>\n'


def build_doc(lesson: dict) -> str:
    n = lesson["n"]
    body = open(os.path.join(DOCS, f"{n:02d}_body.html")).read()
    custom_js_path = os.path.join(DOCS, f"{n:02d}_custom.js")
    custom_js = open(custom_js_path).read() if os.path.exists(custom_js_path) else ""
    title = f"L{n} · {lesson['title']} — documento interactivo"
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n<style>\n{_css()}</style>\n</head>\n'
            f'<body data-lesson="{n:02d}">\n'
            f'{body}\n{_guion_embed(n)}{_doc_data(n)}<script>\n{SHARED_JS}\n{custom_js}\n</script>\n</body>\n</html>\n')


def build_index(lessons: list[dict], root: str) -> str:
    """El índice del curso: 15 tarjetas + progreso local del alumno."""
    cards = []
    for L in lessons:
        n = L["n"]
        slugname = L["slug"].split("-", 1)[1]
        doc = f'{L["slug"]}/presentation/{slugname}-doc.html'
        cards.append(f'''<a class="lcard" href="{doc}" data-lesson="{n:02d}">
  <div class="lc-n">L{n}</div>
  <div class="lc-t">{L["title"]}</div>
  <div class="lc-o">{L["piece"]}</div>
  <div class="lc-bar"><div class="lc-fill"></div></div>
  <div class="lc-meta"><span class="lc-scroll">—</span><span class="lc-quiz">quiz —</span></div>
</a>''')
    checkpoint = ""
    if os.path.exists(os.path.join(root, "06-oop-iii-inheritance", "checkpoint.html")):
        checkpoint = ('<a class="lcard special" href="06-oop-iii-inheritance/checkpoint.html">'
                      '<div class="lc-n">✓</div><div class="lc-t">Checkpoint · fundamentos</div>'
                      '<div class="lc-o">20 preguntas sobre L1-L6 · +1/−0.5</div></a>')
    exam = ('<a class="lcard special" href="15-final-exam/examen.html">'
            '<div class="lc-n">L15</div><div class="lc-t">Examen final</div>'
            '<div class="lc-o">40 preguntas · 40 minutos · +1/−0.5</div></a>')
    body = f'''<header class="hero wrap" id="s0" style="padding-bottom:24px">
  <div class="eyebrow"><b>Algo Trading · ICAI 2026</b> · el curso</div>
  <h1>Un curso, <em>un sistema</em></h1>
  <p class="lede">Quince clases construyendo <code>exchange</code>: un motor de
  microestructura y un framework de estrategias. Tu progreso se guarda en este navegador.</p>
</header>
<main class="wrap" style="padding-bottom:60px">
  <div class="lgrid">{''.join(cards)}{checkpoint}{exam}</div>
  <p style="color:var(--faint);font-size:.85rem;margin-top:26px">Cada clase: documento
  interactivo → <code>NN_build_exercises.ipynb</code> (construcción) →
  <code>NN_auxiliary.ipynb</code> (el gimnasio). Progreso local:
  <button class="btn ghost" id="idx-reset" style="font-size:.7rem;padding:4px 10px">borrar</button></p>
</main>
<footer>Algo Trading ICAI 2026 · Álvaro López Chacarra</footer>
<script>
(function(){{
document.querySelectorAll('.lcard[data-lesson]').forEach(c=>{{
  let d={{}};
  try{{d=JSON.parse(localStorage.getItem('algoTrading.'+c.dataset.lesson)||'{{}}');}}catch(_){{}}
  const pct=d.scroll||0;
  c.querySelector('.lc-fill').style.width=pct+'%';
  c.querySelector('.lc-scroll').textContent=pct>0?('leído '+pct+'%'):'sin empezar';
  if(d.quiz)c.querySelector('.lc-quiz').textContent='quiz '+d.quiz.right+'/'+d.quiz.total;
  if(pct>=90&&d.quiz&&d.quiz.right>=Math.ceil(d.quiz.total*0.6))c.classList.add('done');
}});
document.getElementById('idx-reset').addEventListener('click',()=>{{
  if(!confirm('¿Borrar tu progreso local de todas las clases?'))return;
  for(let i=localStorage.length-1;i>=0;i--){{const k=localStorage.key(i);
    if(k&&k.startsWith('algoTrading.'))localStorage.removeItem(k);}}
  location.reload();
}});
}})();
</script>'''
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>Algo Trading ICAI 2026 — índice del curso</title>\n'
            f'<style>\n{_css()}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n')


def has_doc(n: int) -> bool:
    return os.path.exists(os.path.join(DOCS, f"{n:02d}_body.html"))
