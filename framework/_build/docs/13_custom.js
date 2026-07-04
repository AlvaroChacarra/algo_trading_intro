/* L13 — el MM naive con y sin skew (MMSimulation real, misma semilla) */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA;

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  if(e.detail.stage===1){
    DOC.chart('#k1',[{data:D.noskew.inv,color:'#f87171'}],{zero:true});
    $('#k1n').textContent=`inventario SIN control · máx |inv| = ${D.noskew.maxInv}`;
  }
  if(e.detail.stage===4){
    DOC.chart('#k4',[
      {data:D.noskew.inv,color:'#f87171',width:1.1},
      {data:D.skew.inv,color:'#4ade80',width:1.6},
    ],{zero:true});
    $('#k4s').innerHTML=
      `<div><span style="color:#f87171">sin skew</span><b>maxInv ${D.noskew.maxInv} · PnL ${D.noskew.finalPnl}</b></div>
       <div><span style="color:#4ade80">con skew</span><b>maxInv ${D.skew.maxInv} · PnL ${D.skew.finalPnl}</b></div>`;
  }
});

function show(on){
  const d=on?D.skew:D.noskew, color=on?'#4ade80':'#f87171';
  $('#mm-on').classList.toggle('on',on);
  $('#mm-off').classList.toggle('on',!on);
  DOC.chart('#mm-inv',[{data:d.inv,color}],{zero:true});
  DOC.chart('#mm-pnl',[{data:d.pnl,color:'#22d3ee'}],{zero:true});
  $('#mm-stats').innerHTML=
    `<div><span>PnL final</span><b class="${d.finalPnl>=0?'pos':'neg'}">${d.finalPnl}</b></div>
     <div><span>máx |inventario|</span><b>${d.maxInv}</b></div>`;
  $('#mm-log').textContent=`» MMSimulation(MarketMaker('SIM', quote_size=0.1, half_spread=0.6, inventory_skew=${on?'2.0':'0'}), seed=42).run()`;
}
$('#mm-on').addEventListener('click',()=>show(true));
$('#mm-off').addEventListener('click',()=>show(false));
show(false);
})();
