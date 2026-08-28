(function(){
'use strict';

const contractNode=document.getElementById('pedagogy-contract');
if(!contractNode)return;

let contract;
try{contract=JSON.parse(contractNode.textContent);}catch(error){
  console.error('Invalid pedagogy contract',error);return;
}
if(!contract.scenes||!contract.scenes.length)return;

const body=document.body;
const params=new URLSearchParams(location.search);
const mobileQuery=matchMedia('(max-width: 900px)');
const requestedMode=params.get('mode')==='aula'?'aula':'estudio';
const mode=requestedMode==='aula'&&!mobileQuery.matches?'aula':'estudio';
const isProfessor=params.has('profe');
const routeScopes=isProfessor?['LIVE','LIVE+REQUIRED','ALL']:['LIVE','LIVE+REQUIRED'];
let routeScope='LIVE';
let currentScene=0,currentStage=0,lastInput='pointer';

const esc=value=>String(value).replace(/[&<>"']/g,ch=>({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
})[ch]);
const routeClass=route=>`lr-route-${route.toLowerCase()}`;
const scopeRoutes=()=>routeScope==='ALL'?['LIVE','REQUIRED','OPTIONAL']:
  routeScope==='LIVE+REQUIRED'?['LIVE','REQUIRED']:['LIVE'];
const modeUrl=next=>{
  const q=new URLSearchParams(location.search);q.set('mode',next);
  return `${location.pathname}?${q.toString()}${location.hash}`;
};

const models=contract.scenes.map(scene=>{
  const element=document.getElementById(scene.dom_id);
  if(!element)return null;
  element.classList.add('lr-scene',routeClass(scene.route));
  element.dataset.sceneId=scene.id;
  element.dataset.sceneType=scene.type;
  element.dataset.sceneLayout=scene.layout;
  element.dataset.route=scene.route;
  const stages=(scene.stages||[{id:'stage',route:scene.route}]).map(stage=>({
    ...stage,
    route:stage.route||scene.route,
    step:stage.dom_stage===undefined?null:
      element.querySelector(`.step[data-stage="${stage.dom_stage}"]`),
    figure:stage.dom_stage===undefined?null:
      element.querySelector(`.fig-stage[data-stage="${stage.dom_stage}"]`),
  }));
  stages.forEach(stage=>{
    if(stage.step){stage.step.dataset.route=stage.route;stage.step.classList.add(routeClass(stage.route));}
    if(stage.figure){stage.figure.dataset.route=stage.route;stage.figure.classList.add(routeClass(stage.route));}
  });
  const firstWrap=element.matches('.wrap')?element:element.querySelector(':scope > .wrap');
  if(firstWrap){
    const badge=document.createElement('div');
    badge.className=`lr-scene-badge ${routeClass(scene.route)}`;
    badge.innerHTML=`<span>${esc(scene.route)}</span><span>${esc(scene.type)}</span><span>${scene.duration_minutes} min</span>`;
    firstWrap.insertBefore(badge,firstWrap.firstChild);
  }
  return {...scene,element,stages};
}).filter(Boolean);

if(!models.length)return;
body.classList.add('lr-has-contract',`mode-${mode}`);
body.dataset.learningMode=mode;
body.dataset.requestedMode=requestedMode;
if(requestedMode!==mode)body.classList.add('lr-mobile-fallback');

const nav=document.createElement('aside');
nav.id='lr-nav';
nav.setAttribute('aria-label','Navegación de la lesson');
nav.innerHTML=`
  <div class="lr-brand"><b>L${Number(contract.lesson)}</b><span>${esc(contract.title)}</span></div>
  <div class="lr-modes" aria-label="Modo de lectura">
    <a href="${modeUrl('aula')}" class="${mode==='aula'?'on':''}">Aula</a>
    <a href="${modeUrl('estudio')}" class="${mode==='estudio'?'on':''}">Estudio</a>
  </div>
  ${requestedMode!==mode?'<p class="lr-fallback-note">Aula usa el fallback vertical en esta pantalla.</p>':''}
  <div class="lr-scene-links"></div>`;
body.appendChild(nav);

const navLinks=nav.querySelector('.lr-scene-links');
models.forEach((scene,index)=>{
  const button=document.createElement('button');
  button.type='button';button.dataset.sceneIndex=String(index);
  button.className=routeClass(scene.route);
  button.innerHTML=`<span>${esc(scene.route)}</span><b>${esc(scene.id.replace(/^l\d+-/,''))}</b>`;
  button.addEventListener('click',()=>{
    lastInput='pointer';
    if(mode==='aula')goTo(index,0,false);
    else scene.element.scrollIntoView({behavior:reducedMotion()?'auto':'smooth',block:'start'});
  });
  navLinks.appendChild(button);
});

const controls=document.createElement('div');
controls.id='lr-controls';
controls.innerHTML=`
  <button type="button" class="lr-prev" aria-label="Etapa anterior">← <span>Anterior</span></button>
  <div class="lr-progress" aria-live="polite">
    <b class="lr-scene-progress">Escena</b><span>·</span><b class="lr-stage-progress">Etapa</b>
  </div>
  <button type="button" class="lr-route-scope" aria-label="Cambiar ruta">LIVE</button>
  <button type="button" class="lr-next" aria-label="Etapa siguiente"><span>Siguiente</span> →</button>`;
body.appendChild(controls);

const liveRegion=document.createElement('div');
liveRegion.className='lr-sr-only';liveRegion.setAttribute('aria-live','polite');
body.appendChild(liveRegion);

function reducedMotion(){return matchMedia('(prefers-reduced-motion: reduce)').matches;}
function allowed(scene){return scopeRoutes().includes(scene.route);}
function allowedStages(scene){
  const allowedRoutes=scopeRoutes();
  const stages=scene.stages.filter(stage=>allowedRoutes.includes(stage.route));
  return stages.length?stages:scene.stages.slice(0,1);
}
function availableModels(){return models.filter(allowed);}
function persist(scene,stage){
  if(!window.DOC||!DOC.save)return;
  DOC.save({runtime:{mode,routeScope,scene:scene.id,stage:stage.id,ts:Date.now()}});
}
function restore(){
  try{
    const state=JSON.parse(localStorage.getItem(DOC.key())||'{}').runtime;
    if(!state)return;
    if(routeScopes.includes(state.routeScope))routeScope=state.routeScope;
    const sceneIndex=models.findIndex(scene=>scene.id===state.scene&&allowed(scene));
    if(sceneIndex<0)return;
    const stages=allowedStages(models[sceneIndex]);
    const stageIndex=stages.findIndex(stage=>stage.id===state.stage);
    currentScene=sceneIndex;currentStage=Math.max(stageIndex,0);
  }catch(_error){}
}
function activateStage(scene,stage){
  const allSteps=[...scene.element.querySelectorAll('.scrolly .step')];
  const allFigures=[...scene.element.querySelectorAll('.fig-stage')];
  allSteps.forEach(step=>{
    const active=stage.step===step;
    step.classList.toggle('lr-stage-active',active);
    step.classList.toggle('on',active);
    step.setAttribute('aria-hidden',String(!active));
  });
  allFigures.forEach(figure=>{
    const active=stage.figure===figure;
    figure.classList.toggle('on',active);
    figure.setAttribute('aria-hidden',String(!active));
  });
  const name=scene.element.querySelector('.stage-name');
  if(name){
    const source=stage.step&&stage.step.dataset.name;
    name.textContent=source||stage.id;
  }
  const fig=scene.element.querySelector('.fig');
  if(fig&&stage.dom_stage!==undefined){
    fig.dispatchEvent(new CustomEvent('stagechange',{detail:{stage:stage.dom_stage}}));
  }
}
function syncNav(scene){
  [...navLinks.querySelectorAll('button')].forEach(button=>{
    const index=Number(button.dataset.sceneIndex);
    button.hidden=mode==='aula'&&!allowed(models[index]);
    button.classList.toggle('on',models[index]===scene);
    button.setAttribute('aria-current',models[index]===scene?'step':'false');
  });
}
function goTo(sceneIndex,stageIndex,focusHeading){
  let scene=models[sceneIndex];
  if(!scene||!allowed(scene)){
    scene=availableModels()[0];sceneIndex=models.indexOf(scene);stageIndex=0;
  }
  const stages=allowedStages(scene);
  stageIndex=Math.max(0,Math.min(stageIndex,stages.length-1));
  const stage=stages[stageIndex];
  currentScene=sceneIndex;currentStage=stageIndex;
  models.forEach(model=>{
    const active=model===scene;
    model.element.classList.toggle('lr-scene-active',active);
    model.element.setAttribute('aria-hidden',String(!active));
  });
  activateStage(scene,stage);
  const available=availableModels();
  const scenePosition=available.indexOf(scene)+1;
  controls.querySelector('.lr-scene-progress').textContent=`Escena ${scenePosition}/${available.length}`;
  controls.querySelector('.lr-stage-progress').textContent=`Etapa ${stageIndex+1}/${stages.length}`;
  controls.querySelector('.lr-route-scope').textContent=routeScope;
  controls.querySelector('.lr-prev').disabled=scenePosition===1&&stageIndex===0;
  controls.querySelector('.lr-next').disabled=scenePosition===available.length&&stageIndex===stages.length-1;
  syncNav(scene);persist(scene,stage);
  liveRegion.textContent=`${scene.id}, etapa ${stageIndex+1} de ${stages.length}`;
  if(focusHeading){
    const heading=scene.element.querySelector('h1,h2,h3');
    if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
  }
}
function move(delta,focusHeading=true){
  const scene=models[currentScene],stages=allowedStages(scene);
  if(delta>0&&currentStage<stages.length-1)return goTo(currentScene,currentStage+1,focusHeading);
  if(delta<0&&currentStage>0)return goTo(currentScene,currentStage-1,focusHeading);
  const available=availableModels(),position=available.indexOf(scene);
  const next=available[position+delta];
  if(!next)return;
  const nextIndex=models.indexOf(next),nextStages=allowedStages(next);
  goTo(nextIndex,delta>0?0:nextStages.length-1,focusHeading);
}
function closeOverlays(){
  document.getElementById('guion-drawer')?.classList.remove('open');
  document.querySelectorAll('dialog[open]').forEach(dialog=>dialog.close());
  document.querySelectorAll('[data-overlay].open').forEach(node=>node.classList.remove('open'));
}
function cycleScope(){
  const index=routeScopes.indexOf(routeScope);
  routeScope=routeScopes[(index+1)%routeScopes.length];
  goTo(currentScene,currentStage,false);
}

controls.querySelector('.lr-prev').addEventListener('click',()=>move(-1,false));
controls.querySelector('.lr-next').addEventListener('click',()=>move(1,false));
controls.querySelector('.lr-route-scope').addEventListener('click',cycleScope);

document.addEventListener('keydown',event=>{
  lastInput='keyboard';
  if(event.key==='Escape'){closeOverlays();return;}
  if(mode!=='aula')return;
  const active=document.activeElement;
  if(active&&(/INPUT|TEXTAREA|SELECT/.test(active.tagName)||active.isContentEditable))return;
  if(active&&active.tagName==='BUTTON'&&(event.key===' '||event.key==='Enter'))return;
  if(['ArrowRight','PageDown',' '].includes(event.key)){
    event.preventDefault();move(1,true);
  }else if(['ArrowLeft','PageUp'].includes(event.key)){
    event.preventDefault();move(-1,true);
  }
});

if(mode==='aula'){
  restore();goTo(currentScene,currentStage,false);
}else{
  controls.hidden=true;
  models.forEach(scene=>scene.element.setAttribute('aria-hidden','false'));
  const observer=new IntersectionObserver(entries=>{
    const visible=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
    if(!visible)return;
    const scene=models.find(item=>item.element===visible.target);
    if(scene)syncNav(scene);
  },{rootMargin:'-25% 0px -60% 0px',threshold:[0,.2,.5]});
  models.forEach(scene=>observer.observe(scene.element));
}

mobileQuery.addEventListener?.('change',()=>location.reload());
})();
