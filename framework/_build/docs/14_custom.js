/* L14 — A-S: fórmulas con sliders + barrido calculado de gamma */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA, SIG_H=D.sigmaHorizon, KAP=D.kappa;

/* figura: decaimiento del término de inventario y duelo final */
const decay=[];
for(let t=0;t<=100;t++){const tau=1-t/100;decay.push(1*0.5*SIG_H*SIG_H*tau);}
const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  if(e.detail.stage===3)DOC.chart('#as3',[{data:decay,color:'#fbbf24'}],{zero:true});
  if(e.detail.stage===4){
    DOC.chart('#as4',[
      {data:D.naive.pnl,color:'#5b5b66',width:1.2},
      {data:D.as.pnl,color:'#22d3ee',width:1.8,endDot:true},
    ],{zero:true});
    $('#as4s').innerHTML=
      `<div><span style="color:#5b5b66">naive (L13)</span><b>PnL ${D.naive.finalPnl} · maxInv ${D.naive.maxInv}</b></div>
       <div><span style="color:#22d3ee">A-S (γ=0.5)</span><b>PnL ${D.as.finalPnl} · maxInv ${D.as.maxInv}</b></div>`;
  }
});

/* laboratorio de fórmulas */
function lab(){
  const g=(+$('#lb-g').value)/100, q=(+$('#lb-q').value)/10, tau=(+$('#lb-t').value)/100;
  $('#lb-gv').textContent=g.toFixed(2);
  $('#lb-qv').textContent=q.toFixed(1);
  $('#lb-tv').textContent=tau.toFixed(2);
  const mid=100;
  const r=mid-q*g*SIG_H*SIG_H*tau;
  const d=g*SIG_H*SIG_H*tau+(2/g)*Math.log1p(g/KAP);
  $('#lb-r').textContent=r.toFixed(3);
  $('#lb-d').textContent=d.toFixed(3);
  $('#lb-bq').textContent=`${(r-d/2).toFixed(2)} / ${(r+d/2).toFixed(2)}`;
  $('#lb-log').textContent=`» σ_H=${SIG_H.toFixed(2)} por horizonte · r = 100 − ${q.toFixed(1)}×${g.toFixed(2)}×${(SIG_H*SIG_H).toFixed(2)}×${tau.toFixed(2)}   ·   δ = ${(g*SIG_H*SIG_H*tau).toFixed(3)} + ${((2/g)*Math.log1p(g/KAP)).toFixed(3)}`;
}
['lb-g','lb-q','lb-t'].forEach(id=>$('#'+id).addEventListener('input',lab));
lab();

/* barrido calculado */
$('#sw-tab').textContent='γ        PnL final    máx |inv|\n'
  +D.sweep.map(s=>`${String(s.gamma).padEnd(7)}  ${String(s.pnl).padEnd(11)}  ${s.maxInv}`).join('\n');
})();

/* números data-driven */
(function(){
const s=DOC_DATA.sweep,a=s[0],b=s[s.length-1];
const put=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
put('dd-swi',a.maxInv+'→'+b.maxInv);
put('dd-swp',Math.round(a.pnl)+'→'+Math.round(b.pnl));
})();
