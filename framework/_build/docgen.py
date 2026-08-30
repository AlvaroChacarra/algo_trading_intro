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
import html
import json
import os

HERE = os.path.dirname(__file__)
ASSETS = os.path.join(HERE, "doc_assets")
DOCS = os.path.join(HERE, "docs")
PEDAGOGY = os.path.abspath(os.path.join(HERE, "..", "..", "pedagogy", "lessons"))


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


def _pedagogy_payload(n: int) -> dict:
    path = os.path.join(PEDAGOGY, f"{n:02d}.yml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _runtime_state_counts(payload: dict) -> dict[str, int]:
    """Count navigable states by their effective route (stage overrides scene)."""
    counts = {"LIVE": 0, "REQUIRED": 0, "OPTIONAL": 0}
    for scene in payload.get("scenes", []):
        scene_route = scene.get("route", "LIVE")
        stages = scene.get("stages") or [{"route": scene_route}]
        for stage in stages:
            effective = stage.get("route", scene_route)
            if effective in counts:
                counts[effective] += 1
    return counts


def _pedagogy_contract(n: int) -> str:
    """Embed one lesson contract as JSON; aula and estudio share this source."""
    payload = _pedagogy_payload(n)
    if not payload.get("scenes"):
        return ""
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("</", "<\\/")
    return f'<script type="application/json" id="pedagogy-contract">{text}</script>\n'


def _learning_runtime_js(n: int) -> str:
    if not _pedagogy_payload(n).get("scenes"):
        return ""
    path = os.path.join(ASSETS, "learning_runtime.js")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


SHARED_JS = r"""
(function(){
"use strict";
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── mini-gráficas canvas (compartidas por los docs con datos reproducibles) ── */
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
    if(document.body.classList.contains('lr-modal-open'))return;
    if(document.body.classList.contains('mode-aula'))return;
    if(!['ArrowDown','ArrowUp','PageDown','PageUp'].includes(e.key))return;
    if(/INPUT|TEXTAREA|SELECT|BUTTON/.test(document.activeElement.tagName))return;
    const scroller=document.activeElement?.closest('[data-lr-scroller="true"]');
    if(scroller)return;
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
  const professor=['1','true'].includes(
    (new URLSearchParams(location.search).get('profe')||'').toLowerCase());
  if(!srcEl||!professor)return;
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
  drawer.dataset.overlay='guide';drawer.hidden=true;drawer.inert=true;drawer.setAttribute('inert','');
  drawer.setAttribute('aria-hidden','true');drawer.setAttribute('aria-label','Guion completo del profesor');
  drawer.setAttribute('role','dialog');drawer.setAttribute('aria-modal','true');
  drawer.innerHTML='<div class="gd-head">📋 Guion del profesor'
    +'<button type="button" id="gd-close" aria-label="Cerrar guion">✕</button></div>'
    +'<div class="gd-body" data-lr-scroller="true" data-lr-scroller-axis="vertical" tabindex="0"'
    +' role="region" aria-label="Contenido desplazable del guion completo"><p>'
    +mdlite(srcEl.textContent)+'</p></div>';
  document.body.appendChild(drawer);
  const btn=document.createElement('button');
  btn.id='gd-toggle';btn.className='btn';btn.type='button';btn.textContent='📋 Guion';
  btn.setAttribute('aria-controls','guion-drawer');btn.setAttribute('aria-expanded','false');
  document.body.appendChild(btn);
  let lastTrigger=btn;
  const setOpen=(open,trigger=null,restore=true)=>{
    const currentlyOpen=drawer.classList.contains('open');
    if(open===currentlyOpen)return false;
    if(open){
      window.LEARNING_TEACHER_DRAWER?.close({restoreFocus:false});
      lastTrigger=trigger||document.activeElement||btn;drawer.hidden=false;
      drawer.inert=false;drawer.removeAttribute('inert');
      window.LEARNING_MODAL_BACKGROUND?.(drawer,true);
    }
    drawer.classList.toggle('open',open);drawer.setAttribute('aria-hidden',String(!open));
    btn.setAttribute('aria-expanded',String(open));
    if(open)drawer.querySelector('#gd-close').focus();
    else{
      drawer.hidden=true;drawer.inert=true;drawer.setAttribute('inert','');
      window.LEARNING_MODAL_BACKGROUND?.(drawer,false);
      if(restore)window.LEARNING_RESTORE_FOCUS?.(lastTrigger,btn);
    }
    return true;
  };
  const focusable='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),'
    +'textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
  drawer.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const items=[...drawer.querySelectorAll(focusable)].filter(node=>!node.hidden&&node.getClientRects().length);
    if(!items.length)return;
    const first=items[0],last=items[items.length-1];
    if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
  });
  btn.addEventListener('click',event=>setOpen(true,event.currentTarget));
  drawer.querySelector('#gd-close').addEventListener('click',()=>setOpen(false));
  window.GUIDE_DRAWER={open:trigger=>setOpen(true,trigger),
    close:options=>setOpen(false,null,options?.restoreFocus!==false),
    isOpen:()=>drawer.classList.contains('open')};
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


def _css(n: int | None = None) -> str:
    css = (open(os.path.join(ASSETS, "fonts_embed.css")).read()
           + open(os.path.join(ASSETS, "shared.css")).read()
           + open(os.path.join(ASSETS, "extra.css")).read())
    if n is not None and _pedagogy_payload(n).get("scenes"):
        css += open(os.path.join(ASSETS, "learning_runtime.css")).read()
    return css


def _guion_embed(text: str) -> str:
    """Embed the emitted teacher script (visible only with ``?profe=1``)."""
    if not text:
        raise ValueError("every interactive document requires a teacher script")
    text = text.replace("</script", "<\\/script")
    return f'<script type="text/plain" id="guion-src">{text}</script>\n'


def build_doc(lesson: dict, guion_text: str) -> str:
    n = lesson["n"]
    body = open(os.path.join(DOCS, f"{n:02d}_body.html")).read()
    custom_js_path = os.path.join(DOCS, f"{n:02d}_custom.js")
    custom_js = open(custom_js_path).read() if os.path.exists(custom_js_path) else ""
    runtime_js = _learning_runtime_js(n)
    scripts = f"{SHARED_JS}\n{custom_js}" + (f"\n{runtime_js}" if runtime_js else "")
    title = f"L{n} · {lesson['title']} — documento interactivo"
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n<style>\n{_css(n)}</style>\n</head>\n'
            f'<body data-lesson="{n:02d}">\n'
            f'{body}\n{_guion_embed(guion_text)}{_doc_data(n)}{_pedagogy_contract(n)}'
            f'<script>\n{scripts}\n</script>\n'
            f'</body>\n</html>\n')


INDEX_CSS = r"""
.course-index{max-width:1320px}.course-index-hero{max-width:1100px}
.course-block{padding:28px 0 18px;border-top:1px solid var(--line)}
.course-block:first-child{border-top:0}.course-block-head{display:flex;align-items:end;
  justify-content:space-between;gap:18px;margin-bottom:14px}
.course-block-head h2{margin:0;font-size:1.4rem}.course-flow{color:var(--accent);
  font:600 .72rem var(--mono);letter-spacing:.08em}.course-block-head p{margin:0;
  color:var(--muted);font-size:.86rem;text-align:right}
.lc-load{display:flex;gap:7px;flex-wrap:wrap;margin:9px 0 2px;font:600 .6rem var(--mono)}
.lc-load span{padding:3px 7px;border:1px solid var(--line);border-radius:99px;color:var(--muted)}
.lc-load .live{border-color:rgba(34,211,238,.35);color:var(--accent)}
.lc-load .required{border-color:rgba(192,132,252,.38);color:var(--kw)}
.lc-load .optional{color:var(--faint)}
.lc-route-progress{display:grid;gap:5px;margin:11px 0 7px}
.lc-route-row{display:grid;grid-template-columns:62px minmax(0,1fr) 34px;gap:7px;
  align-items:center;font:600 .58rem var(--mono);color:var(--faint)}
.lc-route-row .lc-bar{margin:0}.lc-route-row.required .lc-fill{background:var(--kw)}
.lc-route-row output{text-align:right;color:var(--muted)}
.lc-dep{margin-top:8px;color:var(--faint);font:500 .62rem var(--mono)}
.lc-meta .lc-status{color:var(--muted)}.lcard.done .lc-status{color:var(--bid)}
.assessment-grid{display:grid;grid-template-columns:minmax(260px,420px);gap:14px}
@media(max-width:700px){.course-block-head{display:block}.course-block-head p{text-align:left;margin-top:5px}
  .course-index{padding-inline:14px}.lgrid{grid-template-columns:1fr}}
"""


def build_index(lessons: list[dict], root: str) -> str:
    """Course map grouped by progression, with route-aware local progress."""
    cards: dict[int, str] = {}
    for lesson in lessons:
        n = lesson["n"]
        payload = _pedagogy_payload(n)
        counts = _runtime_state_counts(payload)
        load = payload.get("load", {})
        live_min = load.get("live_presentation_minutes", 0)
        guided_min = load.get("guided_minutes", 0)
        required_min = load.get("required_autonomous_minutes", 0)
        optional_min = load.get("optional_minutes", 0)
        requires = payload.get("requires", {})
        prerequisite_count = sum(len(requires.get(kind, []))
                                 for kind in ("concepts", "apis", "notation"))
        slugname = lesson["slug"].split("-", 1)[1]
        doc = f'{lesson["slug"]}/presentation/{slugname}-doc.html'
        build = f'{lesson["slug"]}/exercises/{n:02d}_build_exercises.html'
        auxiliary = f'{lesson["slug"]}/exercises/{n:02d}_auxiliary.html'
        optional_chip = (f'<span class="optional">OPTIONAL {optional_min} min</span>'
                         if optional_min else "")
        dependency = ("Punto de entrada" if n == 1 else
                      f"Continúa L{n - 1} · {prerequisite_count} prerrequisitos declarados")
        cards[n] = f'''<article class="lcard" data-lesson="{n:02d}"
  data-live-states="{counts['LIVE']}" data-required-states="{counts['REQUIRED']}">
  <div class="lc-n">L{n}</div>
  <div class="lc-t">{html.escape(lesson["title"])}</div>
  <div class="lc-o">{html.escape(lesson["piece"])}</div>
  <div class="lc-load"><span class="live">LIVE {live_min} + práctica {guided_min} min</span>
    <span class="required">REQUIRED {required_min} min</span>{optional_chip}</div>
  <div class="lc-dep">{dependency}</div>
  <div class="lc-route-progress" aria-label="Progreso por ruta">
    <div class="lc-route-row live"><span>LIVE</span><div class="lc-bar"><div class="lc-fill"></div></div><output>0%</output></div>
    <div class="lc-route-row required"><span>REQUIRED</span><div class="lc-bar"><div class="lc-fill"></div></div><output>0%</output></div>
  </div>
  <div class="lc-meta"><span class="lc-status">sin empezar</span><span class="lc-quiz">quiz —</span></div>
  <nav class="lc-actions" aria-label="Materiales de la clase {n}">
    <a href="{doc}">📖 Documento</a>
    <a href="{build}">🧪 Build exercises</a>
    <a href="{auxiliary}">🏋️ Auxiliary exercises</a>
  </nav>
</article>'''

    checkpoint = ""
    if os.path.exists(os.path.join(root, "06-oop-iii-inheritance", "checkpoint.html")):
        checkpoint = ('<a class="lcard special" href="06-oop-iii-inheritance/checkpoint.html">'
                      '<div class="lc-n">✓</div><div class="lc-t">Checkpoint · fundamentos</div>'
                      '<div class="lc-o">20 preguntas sobre L1-L6 · +1/−0.5</div></a>')
    capstone = ""
    if os.path.exists(os.path.join(root, "14-avellaneda-stoikov", "CAPSTONE.md")):
        capstone = ('<a class="lcard special" href="14-avellaneda-stoikov/CAPSTONE.md">'
                    '<div class="lc-n">🏁</div><div class="lc-t">Capstone · tu market maker</div>'
                    '<div class="lc-o">Proyecto autónomo REQUIRED · feedback formativo · rúbrica 30/40/30</div></a>')
    blocks = [
        ("FOUNDATIONS", "L1 → L6", "Python y objetos nacen para representar el mercado", range(1, 7), checkpoint),
        ("ENGINE", "L7 → L10", "Del snapshot al motor y al runner", range(7, 11), ""),
        ("STRATEGIES", "L11 → L14", "Medir, ejecutar, cotizar y controlar inventario", range(11, 15), capstone),
    ]
    sections = []
    for name, flow, description, numbers, special in blocks:
        content = "".join(cards[n] for n in numbers if n in cards) + special
        sections.append(f'''<section class="course-block" aria-labelledby="block-{name.lower()}">
  <div class="course-block-head"><div><div class="course-flow">{flow}</div>
    <h2 id="block-{name.lower()}">{name}</h2></div><p>{description}</p></div>
  <div class="lgrid">{content}</div>
</section>''')
    exam = ('<a class="lcard special" href="15-final-exam/examen.html">'
            '<div class="lc-n">L15 · PRÁCTICA PÚBLICA</div>'
            '<div class="lc-t">Práctica acumulativa</div>'
            '<div class="lc-o">40 preguntas · 40 minutos · no acredita nota oficial</div></a>')
    sections.append(f'''<section class="course-block" aria-labelledby="block-assessment">
  <div class="course-block-head"><div><div class="course-flow">L15</div>
    <h2 id="block-assessment">ASSESSMENT</h2></div>
    <p>Practica la integración; la evaluación oficial permanece bloqueada: sus bancos
    deberán crearse de nuevo en la futura fuente privada autorizada</p></div>
  <div class="assessment-grid">{exam}</div>
</section>''')

    body = f'''<header class="hero wrap course-index-hero" id="s0" style="padding-bottom:24px">
  <div class="eyebrow"><b>Algo Trading · ICAI 2026</b> · mapa del curso</div>
  <h1>Un curso, <em>un sistema</em></h1>
  <p class="lede">Catorce lessons construyen <code>exchange</code> en tres bloques; L15 permite
  practicar la integración. LIVE y REQUIRED forman el recorrido obligatorio. OPTIONAL solo aparece
  cuando lo eliges.</p>
</header>
<main class="wrap course-index" style="padding-bottom:60px">
  {''.join(sections)}
  <p style="color:var(--faint);font-size:.85rem;margin-top:26px">El progreso registra escenas y
  etapas visitadas por ruta en este navegador; OPTIONAL no condiciona la finalización.
  <button class="btn ghost" id="idx-reset" style="font-size:.7rem;padding:4px 10px">borrar progreso</button></p>
</main>
<footer>Algo Trading ICAI 2026 · Álvaro López Chacarra</footer>
<script>
(function(){{
const clamp=value=>Math.max(0,Math.min(100,Number(value)||0));
document.querySelectorAll('.lcard[data-lesson]').forEach(card=>{{
  let data={{}};
  try{{data=JSON.parse(localStorage.getItem('algoTrading.'+card.dataset.lesson)||'{{}}');}}catch(_){{}}
  const runtime=data.runtime||{{}},progress=runtime.progress||{{}};
  const runtimeAware=runtime.version>=2&&progress.LIVE&&progress.REQUIRED;
  const live=clamp(runtimeAware?progress.LIVE.percent:(data.scroll||0));
  const required=clamp(runtimeAware?progress.REQUIRED.percent:0);
  const rows=card.querySelectorAll('.lc-route-row');
  [[rows[0],live],[rows[1],required]].forEach(([row,pct])=>{{
    row.querySelector('.lc-fill').style.width=pct+'%';row.querySelector('output').value=pct+'%';
  }});
  const started=live>0||required>0;
  card.querySelector('.lc-status').textContent=!started?'sin empezar':
    (live===100&&required===100?'completado':`LIVE ${{live}}% · REQ ${{required}}%`);
  if(data.quiz)card.querySelector('.lc-quiz').textContent='quiz '+data.quiz.right+'/'+data.quiz.total;
  if(live===100&&required===100)card.classList.add('done');
  card.dataset.progressSource=runtimeAware?'runtime':'legacy-scroll';
}});
document.getElementById('idx-reset').addEventListener('click',()=>{{
  if(!confirm('¿Borrar tu progreso local de todas las lessons?'))return;
  for(let i=localStorage.length-1;i>=0;i--){{const key=localStorage.key(i);
    if(key&&key.startsWith('algoTrading.'))localStorage.removeItem(key);}}
  location.reload();
}});
}})();
</script>'''
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>Algo Trading ICAI 2026 — mapa del curso</title>\n'
            f'<style>\n{_css()}\n{INDEX_CSS}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n')


def has_doc(n: int) -> bool:
    return os.path.exists(os.path.join(DOCS, f"{n:02d}_body.html"))
