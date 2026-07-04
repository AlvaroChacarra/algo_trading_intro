/* L9 — el día real reproducido: curva de equity del Backtest de referencia */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const D=DOC_DATA, E=D.equity, F=D.fill;
const mark={i:F.i,v:E[F.i]};

$('#l9-fill').innerHTML=
`<span class="c"># paso ${F.i+1}: la estrategia dispara</span>
fills = market.submit(Order(<span class="s">'BTCUSDT'</span>, <span class="s">'buy'</span>, <span class="num">0.5</span>, MARKET))

<span class="c"># resultado real:</span>
Fill(buy <span class="num">${F.size.toFixed(4)}</span> @ <span class="num">${F.price}</span>)
<span style="color:var(--warn)">llenado parcial: la market no descansa</span>`;

const fig=document.querySelector('.scrolly .fig');
fig.addEventListener('stagechange',e=>{
  if(e.detail.stage===2)DOC.chart('#l9-c2',[{data:E,color:'#22d3ee'}],{zero:true,marks:[mark]});
  if(e.detail.stage===4){
    DOC.chart('#l9-c4',[{data:E,color:'#22d3ee'}],{zero:true,marks:[mark]});
    $('#l9-stats').innerHTML=
      `<div><span>pasos</span><b>${D.steps}</b></div>
       <div><span>fills</span><b>${D.nFills}</b></div>
       <div><span>posición final</span><b>${D.finalPos}</b></div>
       <div><span>equity final</span><b class="${D.finalEquity>=0?'pos':'neg'}">${D.finalEquity}</b></div>`;
  }
});

/* play del día */
let timer=null;
function stop(){clearInterval(timer);timer=null;}
$('#pl-play').addEventListener('click',()=>{
  stop();let i=2;
  $('#pl-play').disabled=true;
  timer=setInterval(()=>{
    i=Math.min(E.length,i+4);
    DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:i,endDot:true}],
      {zero:true,marks:i>F.i?[mark]:[]});
    $('#pl-log').textContent=`» paso ${i}/${E.length} · equity = ${E[i-1]}`
      +(i>F.i?`   (fill en el paso ${F.i+1}: ${F.size.toFixed(4)} @ ${F.price})`:'');
    if(i>=E.length){stop();$('#pl-play').disabled=false;
      $('#pl-log').textContent=`» día completo · equity final = ${D.finalEquity} con posición ${D.finalPos}`;}
  },28);
});
$('#pl-reset').addEventListener('click',()=>{stop();$('#pl-play').disabled=false;
  DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:2}]);$('#pl-log').textContent='pulsa play';});
DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:2}]);
})();
