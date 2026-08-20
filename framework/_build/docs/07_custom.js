/* L7 — raw snapshot → Level → OrderBook; el scrubber conserva los 500 reales. */
(function(){
"use strict";
const $=s=>document.querySelector(s),D=DOC_DATA,S=D.snaps,R=D.raw;
const stateRows=rows=>rows.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
function bookHTML(s){return s.asks.slice().reverse().map(x=>`<div class="row a"><span>ask ${x[0]}</span><small>${x[1].toFixed(3)}</small></div>`).join('')+'<div class="sep"></div>'+s.bids.map(x=>`<div class="row b"><span>bid ${x[0]}</span><small>${x[1].toFixed(3)}</small></div>`).join('');}

$('#l7-raw').innerHTML=stateRows(R.flatMap(x=>[[`bid_price_${x.i}`,x.bidPrice],[`bid_size_${x.i}`,x.bidSize],[`ask_price_${x.i}`,x.askPrice],[`ask_size_${x.i}`,x.askSize]]));
$('#l7-levels').innerHTML=R.slice(0,2).flatMap(x=>[
  `<div class="trace-step ok"><span>Level(${x.bidPrice}, ${x.bidSize})</span><span class="trace-meta">bid ${x.i}</span></div>`,
  `<div class="trace-step ok"><span>Level(${x.askPrice}, ${x.askSize})</span><span class="trace-meta">ask ${x.i}</span></div>`]).join('');
$('#l7-bids').innerHTML=stateRows(R.map(x=>[`Level(${x.bidPrice}, ${x.bidSize})`,'bid']));
$('#l7-asks').innerHTML=stateRows(R.map(x=>[`Level(${x.askPrice}, ${x.askSize})`,'ask']));
$('#l7-sorted').innerHTML=bookHTML(S[0]);
$('#l7-api').innerHTML=stateRows([
  ['book.best_bid',S[0].bids[0][0]],['book.best_ask',S[0].asks[0][0]],
  ['book.depth(BUY, 3)',D.depthBid3],['book.depth(SELL, 3)',D.depthAsk3],
  ['book.imbalance(1)',S[0].imb1],['book.microprice',S[0].micro]
]);

function paint(t){const s=S[t];$('#sc-tv').textContent=t;$('#sc-book').innerHTML=bookHTML(s);
  $('#sc-stats').innerHTML=stateRows([['best bid / ask',`${s.bids[0][0]} / ${s.asks[0][0]}`],['spread',s.spread],['imbalance(1)',s.imb1],['microprice',s.micro]]);
  DOC.chart('#sc-chart',[{data:D.mids,color:'#22d3ee'}],{marks:[{i:t,v:D.mids[t]}]});}
$('#sc-t').addEventListener('input',e=>paint(+e.target.value));paint(0);
const pct=Math.round(100*D.signalUps/D.signalTotal);
$('#out-sig-val').textContent=`${D.signalUps}/${D.signalTotal} → ${pct}% de subidas al tick siguiente`;
})();
