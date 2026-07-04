/* L10 — dos estrategias por el mismo runner (resultados del Backtest real) */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA;

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  if(e.detail.stage===5){
    DOC.chart('#l10-fig',[
      {data:D.buyonce.equity,color:'#22d3ee'},
      {data:D.imbalance.equity,color:'#c084fc'},
    ],{zero:true});
    $('#l10-figstats').innerHTML=
      `<div><span style="color:#22d3ee">BuyOnce</span><b>${D.buyonce.finalEquity} · ${D.buyonce.nFills} fill</b></div>
       <div><span style="color:#c084fc">Imbalance</span><b>${D.imbalance.finalEquity} · ${D.imbalance.nFills} fills</b></div>`;
  }
});

function show(key){
  const d=key==='a'?D.buyonce:D.imbalance;
  const color=key==='a'?'#22d3ee':'#c084fc';
  $('#st-a').classList.toggle('on',key==='a');
  $('#st-b').classList.toggle('on',key==='b');
  DOC.chart('#st-chart',[{data:d.equity,color,endDot:true}],{zero:true});
  $('#st-stats').innerHTML=
    `<div><span>fills</span><b>${d.nFills}</b></div>
     <div><span>posición final</span><b>${d.finalPos}</b></div>
     <div><span>equity final</span><b class="${d.finalEquity>=0?'pos':'neg'}">${d.finalEquity}</b></div>`;
  $('#st-log').textContent=key==='a'
    ?"» result = Backtest(Market.sample(), BuyOnce(0.5)).run()"
    :"» result = Backtest(Market.sample(), ImbalanceStrategy(thr=0.5)).run()   # mismo run()";
}
$('#st-a').addEventListener('click',()=>show('a'));
$('#st-b').addEventListener('click',()=>show('b'));
show('a');
})();
