/* L7 — snapshots reales: figura del scrolly + scrubber temporal */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA, S=D.snaps;

function bookHTML(s){
  return s.asks.slice().reverse().map(l=>`<div class="row a"><span>ask ${l[0]}</span><small>${l[1].toFixed(3)}</small></div>`).join('')
    +'<div class="sep"></div>'
    +s.bids.map(l=>`<div class="row b"><span>bid ${l[0]}</span><small>${l[1].toFixed(3)}</small></div>`).join('');
}

/* figura del scrolly: snapshot 0 con cada lente */
const s0=S[0];
$('#fg-book0').innerHTML=bookHTML(s0);
$('#fg-book1').innerHTML=bookHTML(s0);
$('#fg-sm').innerHTML=`<div><span>spread</span><b>${s0.spread}</b></div><div><span>mid</span><b>${s0.mid}</b></div>`;
$('#fg-imb').innerHTML=`<div><span>imbalance(1)</span><b class="${s0.imb1>0?'pos':'neg'}">${s0.imb1}</b></div>
  <div><span>imbalance(5)</span><b class="${s0.imb5>0?'pos':'neg'}">${s0.imb5}</b></div>`;
$('#fg-imb-note').textContent=s0.imb1*s0.imb5<0
  ?'…y aquí mismo lo ves: el nivel 1 y los 5 primeros no cuentan la misma historia.'
  :'aquí ambos niveles apuntan en la misma dirección — no siempre pasa.';
$('#fg-micro').innerHTML=`<div><span>mid</span><b>${s0.mid}</b></div>
  <div><span>microprice</span><b>${s0.micro}</b></div>
  <div><span>inclinación</span><b class="${s0.micro>s0.mid?'pos':'neg'}">${(s0.micro-s0.mid).toFixed(2)}</b></div>`;
const db=s0.bids.reduce((a,l)=>a+l[1],0), da=s0.asks.reduce((a,l)=>a+l[1],0);
$('#fg-depth').textContent=`book.depth(Side.BUY,  3)  = ${db.toFixed(3)} BTC\nbook.depth(Side.SELL, 3)  = ${da.toFixed(3)} BTC`;

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  if(e.detail.stage===5){
    DOC.chart('#fg-midchart',[{data:D.mids,color:'#22d3ee'}]);
    DOC.chart('#fg-imbchart',[{data:D.imbs,color:'#c084fc'}],{zero:true});
  }
});

/* scrubber */
function paint(t){
  const s=S[t];
  $('#sc-tv').textContent=t;
  $('#sc-book').innerHTML=bookHTML(s);
  $('#sc-stats').innerHTML=
    `<div><span>mid</span><b>${s.mid}</b></div>
     <div><span>spread</span><b>${s.spread}</b></div>
     <div><span>imbalance(1)</span><b class="${s.imb1>0.15?'pos':s.imb1<-0.15?'neg':''}">${s.imb1}</b></div>
     <div><span>imbalance(5)</span><b class="${s.imb5>0.15?'pos':s.imb5<-0.15?'neg':''}">${s.imb5}</b></div>
     <div><span>microprice</span><b>${s.micro}</b></div>`;
  DOC.chart('#sc-chart',[{data:D.mids,color:'#22d3ee'}],{marks:[{i:t,v:D.mids[t]}]});
}
$('#sc-t').addEventListener('input',()=>paint(+$('#sc-t').value));
paint(0);

/* el conteo de la señal */
const pct=Math.round(100*D.signalUps/D.signalTotal);
$('#out-sig-val').textContent=
  `imbalance > 0.3 ocurrió ${D.signalTotal} veces · el mid subió después ${D.signalUps} (${pct}%)`;
})();

/* números data-driven */
(function(){const el=document.getElementById('dd-sigpct');if(el)el.textContent='≈'+Math.round(100*DOC_DATA.signalUps/DOC_DATA.signalTotal)+'%';})();
