/* L8 — execution trace y simulador derivados del MatchingEngine canónico. */
(function(){
"use strict";
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],D=DOC_DATA;
const rows=xs=>xs.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
function bookHTML(book,focus){return book.asks.slice().reverse().map(x=>`<div class="row a" style="${focus==='asks'?'background:rgba(248,113,113,.08)':''}"><span>ask ${x[0]}</span><small>${(+x[1]).toFixed(3)}</small></div>`).join('')+'<div class="sep"></div>'+book.bids.map(x=>`<div class="row b" style="${focus==='bids'?'background:rgba(74,222,128,.08)':''}"><span>bid ${x[0]}</span><small>${(+x[1]).toFixed(3)}</small></div>`).join('');}
const base={bids:D.bids,asks:D.asks};

function paintTraceSide(side){$('#trace-side-book').innerHTML=bookHTML(base,side==='buy'?'asks':'bids');}
$$('#trace-side button').forEach(b=>b.addEventListener('click',()=>{$$('#trace-side button').forEach(x=>x.classList.toggle('on',x===b));paintTraceSide(b.dataset.side);}));paintTraceSide('buy');
const hero=D.scenarios.find(x=>x.key==='buy:market:1:-1');
$('#trace-size').textContent=hero.size;$('#trace-rem0').textContent=hero.size;
const first=hero.planned[0],rem1=hero.size-first[1];
$('#trace-take').innerHTML=rows([['remaining',hero.size],['level.size',first[1]],['take = min(...)',first[1]]]);
$('#trace-after-take').innerHTML=rows([['remaining antes',hero.size],['take',`− ${first[1]}`],['remaining después',rem1.toFixed(3)]]);
$('#trace-plan').innerHTML=hero.planned.map((x,i)=>`<div class="trace-step ${i===0?'active':''}"><span>(${x[0]}, ${x[1].toFixed(3)})</span><span class="trace-meta">nivel ${i+1}</span></div>`).join('');
$('#trace-commit-book').innerHTML=bookHTML(hero.after);$('#trace-fill').textContent=`Fill(price=${first[0]}, size=${first[1].toFixed(3)})`;
$('#trace-rest').textContent=hero.remaining.toFixed(3);

const policy={
 market:[['selección','opposite'],['plan','sin límite'],['commit','fills'],['remanente','cancelar']],
 limit:[['selección','opposite'],['_crosses','precio límite'],['commit','fills'],['remanente','add_limit']],
 ioc:[['selección','opposite'],['_crosses','igual que LIMIT'],['commit','fills'],['remanente','cancelar']],
 fok:[['selección','opposite'],['PLAN','sin mutar'],['VALIDATE','¿llena todo?'],['COMMIT','solo si sí']]
};
const notes={market:'Cruza mientras exista liquidez. Nada descansa.',limit:'La única política que añade el remanente al book.',ioc:'Mismo plan y commit que LIMIT; sin add_limit.',fok:'Si no completa, return [] antes del primer reduce.'};
function paintPolicy(mode){$('#policy-trace').innerHTML=policy[mode].map((x,i)=>`<div class="trace-step ${i===policy[mode].length-1?'active':'ok'}"><span>${x[0]}</span><span class="trace-meta">${x[1]}</span></div>`).join('');$('#policy-note').innerHTML=`<span class="tag">${mode.toUpperCase()}</span>${notes[mode]}`;}
$$('#policy-modes button').forEach(b=>b.addEventListener('click',()=>{$$('#policy-modes button').forEach(x=>x.classList.toggle('on',x===b));paintPolicy(b.dataset.mode);}));paintPolicy('market');

let sim={type:'market',side:'buy',sizeI:1,priceI:1,phase:0};
function scenario(){const pi=sim.type==='market'?-1:sim.priceI;return D.scenarios.find(x=>x.key===`${sim.side}:${sim.type}:${sim.sizeI}:${pi}`);}
function resetPhase(){sim.phase=0;paintSim();}
function paintSim(){const s=scenario();$('#sim-size-v').textContent=s.size;$('#sim-price-row').style.display=sim.type==='market'?'none':'flex';$('#sim-price-v').textContent=s.price??'MKT';
  const phases=[['1 · SELECT','lado contrario'],['2 · PLAN',`${s.planned.length} niveles`],['3 · VALIDATE',sim.type==='fok'?(s.fills.length?'FOK completa':'FOK aborta'):'ok'],['4 · COMMIT',`${s.fills.length} fills`]];
  $('#sim-phases').innerHTML=phases.map((x,i)=>`<div class="trace-step ${i<sim.phase?'ok':i===sim.phase?'active':''}"><span>${x[0]}</span><span class="trace-meta">${x[1]}</span></div>`).join('');
  const committed=sim.phase>=3;$('#sim-book-label').textContent=committed?'after':'before';$('#sim-book').innerHTML=bookHTML(committed?s.after:s.before,sim.phase===0?(sim.side==='buy'?'asks':'bids'):null);
  let detail=[];if(sim.phase===0)detail=[['opposite',sim.side==='buy'?'asks':'bids'],['remaining',s.size]];
  if(sim.phase===1)detail=s.planned.map((x,i)=>[`planned[${i}]`,`${x[1].toFixed(3)} @ ${x[0]}`]).concat([['remaining',s.remaining.toFixed(3)]]);
  if(sim.phase===2)detail=[['policy',sim.type.toUpperCase()],['valid',sim.type==='fok'?(s.fills.length?'sí':'NO → return []'):'sí']];
  if(sim.phase>=3){
    detail=s.fills.map((x,i)=>[`Fill ${i+1}`,`${x[1].toFixed(3)} @ ${x[0]}`]);
    if(s.remaining>1e-9&&sim.type==='limit')detail.push(['remanente',`${s.remaining.toFixed(3)} descansa @ ${s.price}`]);
    if(s.remaining>1e-9&&['market','ioc'].includes(sim.type))detail.push(['remanente',`${s.remaining.toFixed(3)} cancelado`]);
  }
  if(sim.phase>=3&&!s.fills.length)detail=[['fills','[]'],['book','idéntico']];$('#sim-detail').innerHTML=rows(detail);
}
$$('#sim-type button').forEach(b=>b.addEventListener('click',()=>{$$('#sim-type button').forEach(x=>x.classList.toggle('on',x===b));sim.type=b.dataset.type;resetPhase();}));
$$('#sim-side button').forEach(b=>b.addEventListener('click',()=>{$$('#sim-side button').forEach(x=>x.classList.toggle('on',x===b));sim.side=b.dataset.side;resetPhase();}));
$('#sim-size').addEventListener('input',e=>{sim.sizeI=+e.target.value;resetPhase();});$('#sim-price').addEventListener('input',e=>{sim.priceI=+e.target.value;resetPhase();});
$('#sim-next').addEventListener('click',()=>{sim.phase=Math.min(3,sim.phase+1);paintSim();});$('#sim-reset').addEventListener('click',resetPhase);paintSim();
})();
