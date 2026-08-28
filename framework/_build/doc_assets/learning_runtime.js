(function(){
'use strict';

const RUNTIME_VERSION=2;
const ROUTES=['LIVE','REQUIRED','OPTIONAL'];
const contractNode=document.getElementById('pedagogy-contract');
if(!contractNode)return;

let contract;
try{contract=JSON.parse(contractNode.textContent);}catch(error){
  console.error('Invalid pedagogy contract',error);return;
}
if(!Array.isArray(contract.scenes)||!contract.scenes.length)return;

const body=document.body;
const params=new URLSearchParams(location.search);
const mobileQuery=matchMedia('(max-width: 900px)');
const requestedMode=params.get('mode')==='aula'?'aula':'estudio';
const mode=requestedMode==='aula'&&!mobileQuery.matches?'aula':'estudio';
const isProfessor=['1','true'].includes((params.get('profe')||'').toLowerCase());
const routeScopes=mode==='aula'
  ?(isProfessor?['LIVE','LIVE+REQUIRED','ALL']:['LIVE'])
  :['LIVE+REQUIRED','ALL'];
let routeScope=mode==='estudio'?'LIVE+REQUIRED':'LIVE';
if(mode==='estudio'&&params.get('optional')==='1')routeScope='ALL';
let currentScene=0,currentStage=0;

const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
})[ch]);
const slug=value=>String(value||'focus').toLowerCase().replace(/[^a-z0-9-]+/g,'-');
const route=value=>ROUTES.includes(String(value||'').toUpperCase())
  ?String(value).toUpperCase():'LIVE';
const routeClass=value=>`lr-route-${route(value).toLowerCase()}`;
const scopeRoutes=()=>routeScope==='ALL'?ROUTES:
  routeScope==='LIVE+REQUIRED'?['LIVE','REQUIRED']:['LIVE'];
const modeUrl=next=>{
  const q=new URLSearchParams(location.search);q.set('mode',next);
  return `${location.pathname}?${q.toString()}${location.hash}`;
};
const stateKey=(scene,stage)=>`${scene.id}::${stage.id}`;
const reducedMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;

function elementForStage(nodes,value,index,total){
  if(value!==undefined&&value!==null){
    const wanted=String(value);
    return nodes.find(node=>node.dataset.stage===wanted)||null;
  }
  return total===nodes.length?nodes[index]||null:(total===1&&nodes.length===1?nodes[0]:null);
}

const missingScenes=[];
const models=contract.scenes.map(rawScene=>{
  if(!rawScene||!rawScene.id||!rawScene.dom_id)return null;
  const element=document.getElementById(rawScene.dom_id);
  if(!element){missingScenes.push(rawScene.id);return null;}
  const sceneRoute=route(rawScene.route);
  const layout=slug(rawScene.layout);
  element.classList.add('lr-scene',routeClass(sceneRoute),`lr-layout-${layout}`);
  element.dataset.sceneId=rawScene.id;
  element.dataset.sceneType=rawScene.type||'scene';
  element.dataset.sceneLayout=layout;
  element.dataset.layoutApplied='true';
  element.dataset.route=sceneRoute;
  const allSteps=[...element.querySelectorAll('.scrolly .step')];
  const allFigures=[...element.querySelectorAll('.fig-stage')];
  const declared=Array.isArray(rawScene.stages)&&rawScene.stages.length
    ?rawScene.stages:[{id:'stage',route:sceneRoute}];
  const stages=declared.map((rawStage,index)=>{
    const stage={...rawStage};
    stage.id=stage.id||`stage-${index+1}`;
    stage.route=route(stage.route||sceneRoute);
    stage.step=elementForStage(allSteps,stage.dom_stage,index,declared.length);
    stage.figure=elementForStage(allFigures,stage.dom_stage,index,declared.length);
    [stage.step,stage.figure].filter(Boolean).forEach(node=>{
      node.dataset.route=stage.route;node.classList.add(routeClass(stage.route));
    });
    return stage;
  });
  const firstWrap=element.matches('.wrap')?element:element.querySelector(':scope > .wrap');
  if(firstWrap){
    const badge=document.createElement('div');
    badge.className=`lr-scene-badge ${routeClass(sceneRoute)}`;
    const minutes=Number.isFinite(Number(rawScene.duration_minutes))
      ?`<span>${esc(rawScene.duration_minutes)} min</span>`:'';
    badge.innerHTML=`<span>${esc(sceneRoute)}</span><span>${esc(rawScene.type||'scene')}</span>${minutes}`;
    firstWrap.insertBefore(badge,firstWrap.firstChild);
  }
  return {...rawScene,route:sceneRoute,layout,element,stages,allSteps,allFigures};
}).filter(Boolean);

if(missingScenes.length){
  body.dataset.runtimeContractError='missing-scene-dom';
  console.error(`Pedagogy scenes without DOM nodes: ${missingScenes.join(', ')}`);
}
if(!models.length)return;

body.classList.add('lr-has-contract',`mode-${mode}`);
body.dataset.learningMode=mode;
body.dataset.requestedMode=requestedMode;
body.dataset.professorMode=String(isProfessor);
body.dataset.runtimeVersion=String(RUNTIME_VERSION);
document.documentElement.classList.toggle('lr-mode-aula',mode==='aula');
if(requestedMode!==mode)body.classList.add('lr-mobile-fallback');

const inventory=models.flatMap(scene=>scene.stages.map(stage=>({
  key:stateKey(scene,stage),scene,stage,route:stage.route,
})));
const inventoryKeys=new Set(inventory.map(item=>item.key));
const optionalCount=inventory.filter(item=>item.route==='OPTIONAL').length;

function storageKey(){
  if(window.DOC&&typeof DOC.key==='function')return DOC.key();
  return `algoTrading.${body.dataset.lesson||String(contract.lesson||'x').padStart(2,'0')}`;
}
function readSaved(){
  try{return JSON.parse(localStorage.getItem(storageKey())||'{}');}catch(_error){return {};}
}
const initialSaved=readSaved();
const savedRuntime=initialSaved.runtime||{};
if(params.get('optional')!=='1'&&routeScopes.includes(savedRuntime.routeScope)){
  routeScope=savedRuntime.routeScope;
}
const visited=new Set((Array.isArray(savedRuntime.visited)?savedRuntime.visited:[])
  .filter(key=>inventoryKeys.has(key)));
if(savedRuntime.scene&&savedRuntime.stage){
  const prior=inventory.find(item=>item.scene.id===savedRuntime.scene&&item.stage.id===savedRuntime.stage);
  if(prior)visited.add(prior.key);
}

function progressSnapshot(){
  const progress={};
  ROUTES.forEach(routeName=>{
    const states=inventory.filter(item=>item.route===routeName);
    const seen=states.filter(item=>visited.has(item.key)).length;
    progress[routeName]={
      visited:seen,total:states.length,
      percent:states.length?Math.round(100*seen/states.length):100,
      complete:states.length===0||seen===states.length,
    };
  });
  return progress;
}
function saveRuntime(scene=null,stage=null,mark=false){
  if(scene&&stage&&mark)visited.add(stateKey(scene,stage));
  const previous=readSaved().runtime||{};
  const runtime={...previous,version:RUNTIME_VERSION,mode,routeScope,
    visited:[...visited],progress:progressSnapshot(),ts:Date.now()};
  if(scene)runtime.scene=scene.id;
  if(stage)runtime.stage=stage.id;
  if(window.DOC&&typeof DOC.save==='function')DOC.save({runtime});
  else{
    try{localStorage.setItem(storageKey(),JSON.stringify({...readSaved(),runtime}));}catch(_error){}
  }
  body.dataset.runtimeProgress=JSON.stringify(runtime.progress);
}

const nav=document.createElement('aside');
nav.id='lr-nav';
nav.setAttribute('aria-label','Navegación de la lección');
nav.innerHTML=`
  <a class="lr-course-home" href="../../index.html">← Mapa del curso</a>
  <div class="lr-brand"><b>L${Number(contract.lesson)}</b><span>${esc(contract.title)}</span></div>
  <div class="lr-modes" aria-label="Modo de lectura">
    <a href="${modeUrl('aula')}" class="${mode==='aula'?'on':''}">Aula</a>
    <a href="${modeUrl('estudio')}" class="${mode==='estudio'?'on':''}">Estudio</a>
  </div>
  ${requestedMode!==mode?'<p class="lr-fallback-note">Aula usa el recorrido vertical en esta pantalla.</p>':''}
  <button type="button" class="lr-study-optional" aria-pressed="false">Incluir OPTIONAL</button>
  <div class="lr-scene-links"></div>`;
body.appendChild(nav);

const navLinks=nav.querySelector('.lr-scene-links');
models.forEach((scene,index)=>{
  const button=document.createElement('button');
  button.type='button';button.dataset.sceneIndex=String(index);
  button.className=routeClass(scene.route);
  button.innerHTML=`<span>${esc(scene.route)}</span><b>${esc(scene.id.replace(/^l\d+-/,''))}</b>`;
  button.addEventListener('click',()=>{
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
    <span>·</span><b class="lr-route-progress">0%</b>
  </div>
  <button type="button" class="lr-route-scope" aria-label="Cambiar alcance de ruta">LIVE</button>
  <button type="button" class="lr-next" aria-label="Etapa siguiente"><span>Siguiente</span> →</button>`;
body.appendChild(controls);

const mobileToolbar=document.createElement('div');
mobileToolbar.id='lr-mobile-toolbar';
mobileToolbar.innerHTML=`<a href="../../index.html">← Curso</a>
  <span>${requestedMode==='aula'?'Aula → estudio':'Modo estudio'}</span>
  <button type="button" class="lr-study-optional" aria-pressed="false">+ OPTIONAL</button>
  ${isProfessor?'<button type="button" class="lr-mobile-teacher" aria-expanded="false">Guía</button>':''}`;
body.insertBefore(mobileToolbar,body.firstChild);

const liveRegion=document.createElement('div');
liveRegion.className='lr-sr-only';liveRegion.setAttribute('aria-live','polite');
body.appendChild(liveRegion);

let teacherToggle=null,teacherDrawer=null,teacherBody=null,mobileTeacherToggle=null;
if(isProfessor){
  teacherToggle=document.createElement('button');
  teacherToggle.id='lr-teacher-toggle';teacherToggle.type='button';
  teacherToggle.textContent='Guía docente';teacherToggle.setAttribute('aria-expanded','false');
  teacherToggle.setAttribute('aria-controls','lr-teacher-drawer');
  nav.insertBefore(teacherToggle,navLinks);
  mobileTeacherToggle=mobileToolbar.querySelector('.lr-mobile-teacher');
  mobileTeacherToggle?.setAttribute('aria-controls','lr-teacher-drawer');
  teacherDrawer=document.createElement('aside');
  teacherDrawer.id='lr-teacher-drawer';teacherDrawer.dataset.overlay='teacher';
  teacherDrawer.setAttribute('aria-label','Guía docente de la escena');
  teacherDrawer.setAttribute('aria-hidden','true');
  teacherDrawer.innerHTML='<div class="lr-teacher-head"><b>Guía docente</b>'
    +'<button type="button" class="lr-teacher-close" aria-label="Cerrar guía docente">×</button></div>'
    +'<div class="lr-teacher-body"></div>';
  body.appendChild(teacherDrawer);teacherBody=teacherDrawer.querySelector('.lr-teacher-body');
  const toggleTeacher=force=>{
    const open=force===undefined?!teacherDrawer.classList.contains('open'):force;
    teacherDrawer.classList.toggle('open',open);
    teacherDrawer.setAttribute('aria-hidden',String(!open));
    [teacherToggle,mobileTeacherToggle].filter(Boolean)
      .forEach(button=>button.setAttribute('aria-expanded',String(open)));
    if(open)teacherDrawer.querySelector('.lr-teacher-close').focus();
    else (mobileQuery.matches?mobileTeacherToggle:teacherToggle)?.focus();
  };
  teacherToggle.addEventListener('click',()=>toggleTeacher());
  mobileTeacherToggle?.addEventListener('click',()=>toggleTeacher());
  teacherDrawer.querySelector('.lr-teacher-close').addEventListener('click',()=>toggleTeacher(false));
}

function allowedStages(scene){
  const allowedRoutes=scopeRoutes();
  return scene.stages.filter(stage=>allowedRoutes.includes(stage.route));
}
function allowed(scene){
  return scopeRoutes().includes(scene.route)&&allowedStages(scene).length>0;
}
function availableModels(){return models.filter(allowed);}

function activateStage(scene,stage){
  const hasMappedSteps=scene.stages.some(item=>item.step);
  const hasMappedFigures=scene.stages.some(item=>item.figure);
  scene.allSteps.forEach(step=>{
    const model=scene.stages.find(item=>item.step===step);
    const visibleRoute=!model||scopeRoutes().includes(model.route);
    const active=!hasMappedSteps||stage.step===step;
    step.hidden=!visibleRoute;
    step.classList.toggle('lr-stage-active',active&&visibleRoute);
    step.classList.toggle('on',active&&visibleRoute);
    step.setAttribute('aria-hidden',String(!(active&&visibleRoute)));
  });
  scene.allFigures.forEach(figure=>{
    const model=scene.stages.find(item=>item.figure===figure);
    const visibleRoute=!model||scopeRoutes().includes(model.route);
    const active=!hasMappedFigures||stage.figure===figure;
    figure.hidden=!visibleRoute;
    figure.classList.toggle('on',active&&visibleRoute);
    figure.setAttribute('aria-hidden',String(!(active&&visibleRoute)));
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
function syncNav(scene=null){
  [...navLinks.querySelectorAll('button')].forEach(button=>{
    const index=Number(button.dataset.sceneIndex),model=models[index];
    button.hidden=!allowed(model);
    button.classList.toggle('on',model===scene);
    button.setAttribute('aria-current',model===scene?'step':'false');
  });
}
function notesHtml(value){
  if(!value)return '';
  const values=Array.isArray(value)?value:[value];
  return `<ul>${values.map(item=>`<li>${esc(typeof item==='string'?item:JSON.stringify(item))}</li>`).join('')}</ul>`;
}
function syncTeacher(scene,stage){
  if(!teacherBody||!scene||!stage)return;
  const concepts=scene.concepts||[];
  const objectives=(contract.objectives||[]).filter(objective=>
    (objective.concepts||[]).some(concept=>concepts.includes(concept)));
  const sceneNotes=scene.professor_notes||scene.teacher_notes||scene.teaching_notes;
  const stageNotes=stage.professor_notes||stage.teacher_notes||stage.teaching_notes;
  const fullGuide=document.getElementById('gd-toggle');
  teacherBody.innerHTML=`<p class="lr-teacher-kicker">${esc(scene.route)} · ${esc(scene.type)} · ${esc(scene.duration_minutes)} min</p>`
    +`<h2>${esc(scene.id)}</h2><p class="lr-teacher-stage">Etapa <code>${esc(stage.id)}</code> · layout <code>${esc(scene.layout)}</code></p>`
    +`<h3>Conceptos</h3><ul>${concepts.length?concepts.map(concept=>`<li><code>${esc(concept)}</code></li>`).join(''):'<li>Ninguno declarado.</li>'}</ul>`
    +`<h3>Objetivos relacionados</h3><ul>${objectives.length?objectives.map(objective=>
      `<li><code>${esc(objective.id)}</code> · ${esc(objective.route)}</li>`).join(''):'<li>Ninguno declarado para esta escena.</li>'}</ul>`
    +(sceneNotes?`<h3>Notas de escena</h3>${notesHtml(sceneNotes)}`:'')
    +(stageNotes?`<h3>Notas de etapa</h3>${notesHtml(stageNotes)}`:'')
    +(fullGuide?'<button type="button" class="lr-full-guide">Abrir guion completo</button>':'');
  teacherBody.querySelector('.lr-full-guide')?.addEventListener('click',()=>{
    teacherDrawer.classList.remove('open');teacherDrawer.setAttribute('aria-hidden','true');
    [teacherToggle,mobileTeacherToggle].filter(Boolean)
      .forEach(button=>button.setAttribute('aria-expanded','false'));
    fullGuide.click();
  });
}
function updateDeepLink(scene,stage){
  if(!history.replaceState)return;
  const next=`#${encodeURIComponent(scene.id)}/${encodeURIComponent(stage.id)}`;
  if(location.hash!==next)history.replaceState(null,'',`${location.pathname}${location.search}${next}`);
}
function goTo(sceneIndex,stageIndex,focusHeading=true){
  let scene=models[sceneIndex];
  if(!scene||!allowed(scene)){
    scene=availableModels()[0];sceneIndex=models.indexOf(scene);stageIndex=0;
  }
  if(!scene)return;
  const stages=allowedStages(scene);
  stageIndex=Math.max(0,Math.min(Number(stageIndex)||0,stages.length-1));
  const stage=stages[stageIndex];
  currentScene=sceneIndex;currentStage=stageIndex;
  body.dataset.currentSceneId=scene.id;
  body.dataset.currentStageId=stage.id;
  body.dataset.currentStageRoute=stage.route;
  body.dataset.currentLayout=scene.layout;
  body.dataset.routeScope=routeScope;
  scene.element.dataset.currentStageId=stage.id;
  models.forEach(model=>{
    const active=model===scene;
    model.element.classList.toggle('lr-scene-active',active);
    model.element.setAttribute('aria-hidden',String(!active));
  });
  activateStage(scene,stage);
  const available=availableModels();
  const scenePosition=available.indexOf(scene)+1;
  const flatStates=available.flatMap(model=>allowedStages(model).map(item=>({scene:model,stage:item})));
  const statePosition=flatStates.findIndex(item=>item.scene===scene&&item.stage===stage);
  controls.querySelector('.lr-scene-progress').textContent=`Escena ${scenePosition}/${available.length}`;
  controls.querySelector('.lr-stage-progress').textContent=`Etapa ${stageIndex+1}/${stages.length}`;
  controls.querySelector('.lr-route-scope').textContent=routeScope;
  controls.querySelector('.lr-prev').disabled=statePosition<=0;
  controls.querySelector('.lr-next').disabled=statePosition===flatStates.length-1;
  saveRuntime(scene,stage,true);
  const scopeProgress=progressSnapshot(),enabledRoutes=scopeRoutes();
  const routeProgress=Math.round(enabledRoutes.reduce((total,routeName)=>
    total+scopeProgress[routeName].visited,0)/Math.max(1,enabledRoutes.reduce((total,routeName)=>
    total+scopeProgress[routeName].total,0))*100);
  controls.querySelector('.lr-route-progress').textContent=`${routeProgress}% visto`;
  syncNav(scene);syncTeacher(scene,stage);updateDeepLink(scene,stage);
  liveRegion.textContent=`${scene.id}, etapa ${stageIndex+1} de ${stages.length}`;
  if(focusHeading){
    const heading=scene.element.querySelector('h1,h2,h3');
    if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
  }
}
function move(delta,focusHeading=true){
  const scene=models[currentScene];
  if(!scene)return;
  const stages=allowedStages(scene);
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
  teacherDrawer?.classList.remove('open');
  teacherDrawer?.setAttribute('aria-hidden','true');
  [teacherToggle,mobileTeacherToggle].filter(Boolean)
    .forEach(button=>button.setAttribute('aria-expanded','false'));
  document.querySelectorAll('dialog[open]').forEach(dialog=>dialog.close());
  document.querySelectorAll('[data-overlay].open').forEach(node=>node.classList.remove('open'));
}
function cycleScope(){
  if(routeScopes.length<2)return;
  const scene=models[currentScene];
  const stageId=body.dataset.currentStageId;
  const index=routeScopes.indexOf(routeScope);
  routeScope=routeScopes[(index+1)%routeScopes.length];
  const stages=scene&&allowed(scene)?allowedStages(scene):[];
  const stageIndex=stages.findIndex(stage=>stage.id===stageId);
  goTo(currentScene,Math.max(0,stageIndex),false);
}
function syncOptionalControls(){
  document.querySelectorAll('.lr-study-optional').forEach(button=>{
    button.hidden=mode!=='estudio'||optionalCount===0;
    button.setAttribute('aria-pressed',String(routeScope==='ALL'));
    button.textContent=routeScope==='ALL'?'Ocultar OPTIONAL':
      (button.closest('#lr-mobile-toolbar')?'+ OPTIONAL':'Incluir OPTIONAL');
  });
}
function applyStudyScope(activeScene=null){
  body.dataset.routeScope=routeScope;
  models.forEach(scene=>{
    const sceneVisible=allowed(scene);
    scene.element.hidden=!sceneVisible;
    scene.element.setAttribute('aria-hidden',String(!sceneVisible));
    scene.stages.forEach(stage=>{
      const stageVisible=scopeRoutes().includes(stage.route);
      [stage.step,stage.figure].filter(Boolean).forEach(node=>{
        node.hidden=!stageVisible;node.setAttribute('aria-hidden',String(!stageVisible));
      });
    });
  });
  syncNav(activeScene);syncOptionalControls();saveRuntime(null,null,false);
}
function toggleOptional(){
  routeScope=routeScope==='ALL'?'LIVE+REQUIRED':'ALL';
  applyStudyScope();
  liveRegion.textContent=routeScope==='ALL'?'Contenido OPTIONAL incluido.':'Contenido OPTIONAL oculto.';
}

controls.querySelector('.lr-prev').addEventListener('click',()=>move(-1,false));
controls.querySelector('.lr-next').addEventListener('click',()=>move(1,false));
controls.querySelector('.lr-route-scope').addEventListener('click',cycleScope);
controls.querySelector('.lr-route-scope').hidden=mode!=='aula'||routeScopes.length<2;
controls.classList.toggle('lr-fixed-scope',controls.querySelector('.lr-route-scope').hidden);
document.querySelectorAll('.lr-study-optional').forEach(button=>button.addEventListener('click',toggleOptional));

document.addEventListener('keydown',event=>{
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

function deepLink(){
  let sceneId=params.get('scene'),stageId=params.get('stage');
  if(location.hash){
    const [rawScene,rawStage]=location.hash.slice(1).split('/');
    try{sceneId=decodeURIComponent(rawScene)||sceneId;stageId=decodeURIComponent(rawStage||'')||stageId;}
    catch(_error){sceneId=rawScene||sceneId;stageId=rawStage||stageId;}
  }
  if(!sceneId)return null;
  const scene=models.find(item=>item.id===sceneId||item.dom_id===sceneId);
  if(!scene)return null;
  const stage=scene.stages.find(item=>item.id===stageId)||scene.stages[0];
  return {scene,stage};
}
function restoredPosition(){
  const linked=deepLink();
  if(linked){
    if(mode==='estudio'&&linked.stage.route==='OPTIONAL')routeScope='ALL';
    return linked;
  }
  if(!savedRuntime.scene)return null;
  const scene=models.find(item=>item.id===savedRuntime.scene);
  const stage=scene?.stages.find(item=>item.id===savedRuntime.stage);
  return scene&&stage?{scene,stage}:null;
}

if(mode==='aula'){
  const restored=restoredPosition();
  if(restored&&allowed(restored.scene)&&scopeRoutes().includes(restored.stage.route)){
    currentScene=models.indexOf(restored.scene);
    currentStage=allowedStages(restored.scene).indexOf(restored.stage);
  }
  goTo(currentScene,Math.max(0,currentStage),false);
}else{
  const restored=restoredPosition();
  if(restored?.stage.route==='OPTIONAL')routeScope='ALL';
  applyStudyScope(restored?.scene||null);
  const sceneObserver=new IntersectionObserver(entries=>{
    const visible=entries.filter(entry=>entry.isIntersecting&&!entry.target.hidden)
      .sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
    if(!visible)return;
    const scene=models.find(item=>item.element===visible.target);
    if(!scene)return;
    syncNav(scene);
    const stage=allowedStages(scene).find(item=>!item.step)||allowedStages(scene)[0];
    if(stage){saveRuntime(scene,stage,true);updateDeepLink(scene,stage);}
  },{rootMargin:'-20% 0px -55% 0px',threshold:[0,.15,.4]});
  models.forEach(scene=>sceneObserver.observe(scene.element));
  models.forEach(scene=>scene.stages.forEach(stage=>{
    if(!stage.step)return;
    const observer=new IntersectionObserver(entries=>{
      if(entries.some(entry=>entry.isIntersecting)&&!stage.step.hidden){
        saveRuntime(scene,stage,true);syncNav(scene);updateDeepLink(scene,stage);
      }
    },{rootMargin:'-35% 0px -45% 0px',threshold:.1});
    observer.observe(stage.step);
  }));
  if(restored&&allowed(restored.scene))requestAnimationFrame(()=>{
    (restored.stage.step||restored.scene.element).scrollIntoView({block:'center'});
  });
}

syncOptionalControls();
saveRuntime(null,null,false);
window.LEARNING_RUNTIME={
  version:RUNTIME_VERSION,contract,mode,isProfessor,
  getState:()=>({routeScope,scene:models[currentScene]?.id,stage:body.dataset.currentStageId,
    progress:progressSnapshot()}),
  setOptional:enabled=>{if(mode==='estudio'&&(enabled!==(routeScope==='ALL')))toggleOptional();},
  goTo:(sceneId,stageId)=>{
    const scene=models.find(item=>item.id===sceneId);if(!scene)return false;
    if(mode==='estudio'){
      const stage=scene.stages.find(item=>item.id===stageId)||allowedStages(scene)[0];
      if(!stage)return false;
      (stage.step||scene.element).scrollIntoView({block:'center'});return true;
    }
    const stages=allowedStages(scene),index=stages.findIndex(item=>item.id===stageId);
    goTo(models.indexOf(scene),Math.max(0,index),false);return true;
  },
};

mobileQuery.addEventListener?.('change',()=>location.reload());
})();
