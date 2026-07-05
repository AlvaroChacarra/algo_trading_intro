/* L8 — barridos reales del MatchingEngine sobre el snapshot */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA;

function bookHTML(asks,bids,eaten={}){
  const row=(side,p,s,orig)=>{const left=Math.max(0,orig-(eaten[p]||0));
    const gone=left<=1e-9;
    return `<div class="row ${side}" style="${gone?'opacity:.25;text-decoration:line-through':''}">
      <span>${side==='a'?'ask':'bid'} ${p}</span><small>${left.toFixed(3)}${(eaten[p]&&!gone)?' ←':''}</small></div>`;};
  return asks.slice().reverse().map(l=>row('a',l[0],l[1],l[1])).join('')
    +'<div class="sep"></div>'
    +bids.map(l=>row('b',l[0],l[1],l[1])).join('');
}
function bookAfter(sweep){
  const eaten={};sweep.fills.forEach(f=>eaten[f[0]]=(eaten[f[0]]||0)+f[1]);
  return bookHTML(D.asks,D.bids,eaten);
}

/* figura del scrolly: usa el 3er barrido (3 niveles) como protagonista */
const hero=D.sweeps[2];
$('#m0').innerHTML=bookHTML(D.asks,D.bids);
const eat1={};eat1[D.asks[0][0]]=D.asks[0][1];
$('#m1').innerHTML=bookHTML(D.asks,D.bids,eat1);
$('#m1log').textContent=`» fill 1: ${hero.fills[0][1].toFixed(3)} @ ${hero.fills[0][0]} — el nivel 1, entero`;
$('#m2').innerHTML=bookAfter(hero);
$('#m2log').textContent=`» ${hero.fills.length} fills — la orden barrió ${hero.fills.length} niveles`;
$('#m3stats').innerHTML=
  `<div><span>mid antes</span><b>${D.mid}</b></div>
   <div><span>precio efectivo</span><b>${hero.eff}</b></div>
   <div><span>slippage</span><b class="neg">+${hero.slip}</b></div>`;
$('#m3fills').textContent=hero.fills.map((f,i)=>`fill ${i+1}:  ${f[1].toFixed(3)} @ ${f[0]}`).join('\n');
$('#m4').innerHTML=bookAfter(hero);
$('#m4note').textContent='los niveles consumidos ya no están: el siguiente comprador empieza más arriba';
$('#m5tab').textContent='size      efectivo     slippage\n'
  +D.sweeps.map(s=>`${String(s.size).padEnd(8)}  ${s.eff}   +${s.slip}`).join('\n');

/* simulador de disparos */
const btns=$('#sw-btns');
D.sweeps.forEach((s,i)=>{
  const b=document.createElement('button');
  b.className='btn';b.textContent=`▶ buy ${s.size} BTC`;
  b.addEventListener('click',()=>fire(i));
  btns.appendChild(b);
});
const reset=document.createElement('button');
reset.className='btn ghost';reset.textContent='↻ libro intacto';
reset.addEventListener('click',()=>{paintIdle();});
btns.appendChild(reset);

function paintIdle(){
  $('#sw-book').innerHTML=bookHTML(D.asks,D.bids);
  $('#sw-fills').textContent='';
  $('#sw-stats').innerHTML='';
  $('#sw-log').textContent='elige un tamaño y dispara';
}
function fire(i){
  const s=D.sweeps[i];
  $('#sw-book').innerHTML=bookAfter(s);
  const lines=s.fills.map((f,k)=>`fill ${k+1}:  ${f[1].toFixed(3)} @ ${f[0]}`);
  if(s.filled<s.size-1e-9)lines.push(`(sin llenar: ${(s.size-s.filled).toFixed(3)} — cancelado)`);
  const pre=$('#sw-fills');pre.textContent='';
  s.fills.forEach((_,k)=>setTimeout(()=>{pre.textContent=lines.slice(0,k+1).join('\n');},220*(k+1)));
  setTimeout(()=>{pre.textContent=lines.join('\n');
    $('#sw-stats').innerHTML=
      `<div><span>llenado</span><b>${s.filled} / ${s.size}</b></div>
       <div><span>efectivo</span><b>${s.eff}</b></div>
       <div><span>slippage vs mid</span><b class="neg">+${s.slip}</b></div>`;
  },220*(s.fills.length+1));
  $('#sw-log').textContent=`» fills = engine.process(Order('BTCUSDT', 'buy', ${s.size}, order_type=MARKET), book)`;
}
paintIdle();

/* variantes */
$('#v-big').textContent=D.big;
$('#v-limit').innerHTML=`llenó <b>${D.variants.limit.filled}</b> · descansan <b style="color:var(--bid)">${D.variants.limit.rest}</b> @ ${D.limPx}`;
$('#v-ioc').innerHTML=`llenó <b>${D.variants.ioc.filled}</b> · descansa <b>0</b>`;
$('#v-fok').innerHTML=`llenó <b style="color:var(--ask)">${D.variants.fok.filled}</b> · ${D.variants.fok.nfills} fills`;
})();

/* números data-driven */
(function(){const s=DOC_DATA.sweeps;const put=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};put('dd-slo','+'+s[0].slip);put('dd-shi','+'+s[s.length-1].slip);})();
