/* L12 — hachazo vs TWAP vs VWAP (ejecuciones reales del Backtest) */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA;

$('#hero-total').textContent=D.total;
$('#fig-total').textContent=D.total;

function bars(el,weights,color){
  const mx=Math.max(...weights);
  el.innerHTML=weights.map(w=>
    `<div style="flex:1;background:${color};opacity:.85;border-radius:2px 2px 0 0;height:${Math.max(3,100*w/mx)}%"></div>`).join('');
}

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  const st=e.detail.stage;
  if(st===0)$('#v0').innerHTML=
    `<div><span>mid antes</span><b>${D.mid0}</b></div>
     <div><span>precio medio</span><b class="neg">${D.sweepAvg}</b></div>
     <div><span>coste vs mid</span><b class="neg">${D.sweepCostBps} bps</b></div>`;
  if(st===1)$('#v1').textContent=
`total:      ${D.total} BTC
de golpe:   1 orden  → barre el libro
troceado: 500 trozos → cada uno casi
                       invisible`;
  if(st===2)bars($('#v2bars'),D.bars.map(()=>1),'#5b5b66');
  if(st===3)bars($('#v3bars'),D.bars,'#22d3ee');
  if(st===4)$('#v4').textContent=
`               precio medio   vs mid
de golpe        ${D.sweepAvg}   ${-D.sweepCostBps} bps
TWAP            ${D.twapAvg}   ${-D.twapCostBps} bps
VWAP (perfil U) ${D.vwapAvg}   ${-D.vwapCostBps} bps`;
});

/* duelo */
function show(key){
  $('#pw-twap').classList.toggle('on',key==='twap');
  $('#pw-vwap').classList.toggle('on',key==='vwap');
  if(key==='twap'){bars($('#pw-bars'),D.bars.map(()=>1),'#5b5b66');}
  else{bars($('#pw-bars'),D.bars,'#22d3ee');}
  const avg=key==='twap'?D.twapAvg:D.vwapAvg;
  const cost=key==='twap'?D.twapCostBps:D.vwapCostBps;
  $('#pw-stats').innerHTML=
    `<div><span>precio medio conseguido</span><b>${avg}</b></div>
     <div><span>vs mid inicial (${D.mid0})</span><b class="${cost<0?'pos':'neg'}">${-cost} bps</b></div>
     <div><span>vs el hachazo (${D.sweepAvg})</span><b class="pos">+${(avg-D.sweepAvg).toFixed(2)}</b></div>`;
  $('#pw-log').textContent=key==='twap'
    ?"» VWAPStrategy('BTCUSDT', 'sell', total, 500)              # sin perfil → TWAP"
    :"» VWAPStrategy('BTCUSDT', 'sell', total, 500, perfil_en_U)  # VWAP";
}
$('#pw-twap').addEventListener('click',()=>show('twap'));
$('#pw-vwap').addEventListener('click',()=>show('vwap'));
show('twap');

/* §3½ — predecir el volumen: honesto sobre datos estacionarios */
(function(){
  const vol=D.vol,k=D.rollK;
  $('#pv-k').textContent=k;
  $('#pv-oracle').textContent=D.oracleVsTwapBps;
  // predicciones alineadas al eje X (longitud = nº de barras)
  const staticLine=[vol[0]].concat(D.staticPred);
  const rollLine=[vol[0]].concat(D.rollPred);
  function draw(mode){
    $('#pv-static').classList.toggle('on',mode==='static');
    $('#pv-roll').classList.toggle('on',mode==='roll');
    const pred=mode==='static'?staticLine:rollLine;
    DOC.chart('#pv-chart',[
      {data:vol,color:'#5b5b66',width:1.4},
      {data:pred,color:'#22d3ee',width:2,endDot:true}
    ]);
    const mae=mode==='static'?D.maeStatic:D.maeRoll;
    const other=mode==='static'?D.maeRoll:D.maeStatic;
    const better=mae<=other;
    $('#pv-stats').innerHTML=
      `<div><span>error medio (MAE)</span><b class="${better?'pos':'neg'}">${mae}</b></div>
       <div><span>el otro predictor</span><b>${other}</b></div>
       <div><span>oráculo vs TWAP</span><b>${D.oracleVsTwapBps} bps</b></div>`;
    $('#pv-log').textContent=mode==='static'
      ? 'pred[i] = media(todo el histórico) = '+D.volMean+'    # el perfil fijo, imbatible aquí'
      : 'pred[i] = media(vol[i-'+k+' : i])                    # se adapta… a ruido';
  }
  $('#pv-static').addEventListener('click',()=>draw('static'));
  $('#pv-roll').addEventListener('click',()=>draw('roll'));
  draw('static');
})();
})();
