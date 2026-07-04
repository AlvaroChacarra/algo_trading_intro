/* L6 — polimorfismo vivo: una llamada, tres respuestas */
(function(){
"use strict";
const $=s=>document.querySelector(s);
function decide(strat, imb){
  if(strat==='base')return 'hold';
  if(strat==='momentum')return imb>0.6?'buy':imb<0.4?'sell':'hold';
  /* contraria */
  return imb>0.6?'sell':imb<0.4?'buy':'hold';
}
function paint(id, d){
  const el=$(id);
  el.textContent=`decide(book) → '${d}'`;
  el.className='dec '+d;
}
function update(){
  const imb=(+$('#pf-imb').value)/100;
  $('#pf-imbv').textContent=imb.toFixed(2);
  const ds=['base','momentum','contraria'].map(s=>decide(s,imb));
  paint('#pf-d0',ds[0]);paint('#pf-d1',ds[1]);paint('#pf-d2',ds[2]);
  $('#pf-log').textContent=`» for s in familia: s.decide(book)   # imbalance=${imb.toFixed(2)} → ${ds.join(' · ')}`;
}
$('#pf-imb').addEventListener('input',update);
update();
})();
