/* L11 — señal vs monos, arrival mid y la autopsia del coste (datos reales) */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA, SIG=D.signal;
const GRAY=['#5b5b66','#4a4a55','#6b6b78'];
const cost=D.avgSlip*D.nSlips*0.05;
const gross=SIG.finalEquity+cost;

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  const st=e.detail.stage;
  if(st===0){
    DOC.chart('#j0',[{data:SIG.equity,color:'#22d3ee',endDot:true}],{zero:true});
    $('#j0s').innerHTML=`<div><span>fills</span><b>${SIG.nFills}</b></div>
      <div><span>equity final</span><b class="neg">${SIG.finalEquity}</b></div>
      <div><span>¿bueno?</span><b>¿comparado con qué?</b></div>`;
  }
  if(st===1){
    DOC.chart('#j1',[
      ...D.monos.map((m,i)=>({data:m,color:GRAY[i],width:1.1})),
      {data:SIG.equity,color:'#22d3ee',width:1.8},
    ],{zero:true});
    $('#j1n').textContent=`monos (equity final): ${D.monoFinals.join('  ·  ')} — misma munición, cero señal`;
  }
  if(st===2){
    $('#j2').innerHTML=`<div><span>arrival mid</span><b>${D.arrivalMid}</b></div>
      <div><span>slippage medio</span><b class="neg">+${D.avgSlip}</b></div>
      <div><span>coste ≈</span><b class="neg">${cost.toFixed(1)}</b></div>`;
  }
  if(st===3){
    $('#j3').textContent=`posición final:   ${SIG.finalPos} BTC\nexposición:       tu equity se movió con BTC\n                  durante todo el día`;
  }
  if(st===4){
    $('#j4').textContent=
`equity final:      ${SIG.finalEquity}
coste ejecución:  ≈ ${cost.toFixed(1)}
"bruto" sin peaje: ≈ ${gross.toFixed(1)}

veredicto: la idea respira;
la ejecución la estranguló.`;
  }
});

/* monos on/off */
let monos=false;
function paint(){
  const series=[{data:SIG.equity,color:'#22d3ee',width:1.8,endDot:true}];
  if(monos)D.monos.forEach((m,i)=>series.unshift({data:m,color:GRAY[i],width:1.1}));
  DOC.chart('#mn-chart',series,{zero:true});
  $('#mn-log').textContent=monos
    ?`» señal: ${SIG.finalEquity}  ·  monos: ${D.monoFinals.join(' · ')} — ¿estás fuera de la nube?`
    :`» señal sola: ${SIG.finalEquity}. Sin contexto, no significa nada todavía.`;
  $('#mn-toggle').textContent=monos?'✕ Quitar los monos':'▶ Soltar los monos';
}
$('#mn-toggle').addEventListener('click',()=>{monos=!monos;paint();});
paint();

$('#out-cost-val').textContent=
  `${D.avgSlip} × ${D.nSlips} × 0.05 ≈ ${cost.toFixed(1)}   # vs pérdida total de ${Math.abs(SIG.finalEquity)}`;
})();
