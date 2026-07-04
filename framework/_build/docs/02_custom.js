/* L2 — simulador del libro vivo: cada botón llama a "tus" funciones */
(function(){
"use strict";
const $=s=>document.querySelector(s);
let book=[], nextId=1;
const bidPool=[[99950,0.5],[99940,0.2],[99960,0.3],[99930,0.4]];
const askPool=[[100000,0.3],[100010,0.15],[99990,0.25],[100020,0.5]];
let bi=0, ai=0;

function bestBid(){const p=book.filter(o=>o.side==='buy').map(o=>o.price);return p.length?Math.max(...p):null;}
function bestAsk(){const p=book.filter(o=>o.side==='sell').map(o=>o.price);return p.length?Math.min(...p):null;}
function imbalance(){
  const b=book.filter(o=>o.side==='buy').reduce((s,o)=>s+o.size,0);
  const a=book.filter(o=>o.side==='sell').reduce((s,o)=>s+o.size,0);
  return (b+a)>0?b/(b+a):null;
}
function fmtF(x){return Number.isInteger(x)?x+'.0':String(Math.round(x*10000)/10000);}

function render(){
  const el=$('#lb-book');
  if(!book.length){el.innerHTML='<p style="color:var(--faint);font-size:.8rem">— book = [] —</p>';}
  else{
    const asks=book.filter(o=>o.side==='sell').sort((x,y)=>y.price-x.price);
    const bids=book.filter(o=>o.side==='buy').sort((x,y)=>y.price-x.price);
    el.innerHTML=asks.map(o=>`<div class="row a"><span>sell ${o.price}</span><small>${o.size.toFixed(2)} · id=${o.id}</small></div>`).join('')
      +(asks.length&&bids.length?'<div class="sep"></div>':'')
      +bids.map(o=>`<div class="row b"><span>buy&nbsp; ${o.price}</span><small>${o.size.toFixed(2)} · id=${o.id}</small></div>`).join('');
  }
  const bb=bestBid(), ba=bestAsk(), imb=imbalance();
  $('#lb-bb').textContent=bb??'—';
  $('#lb-ba').textContent=ba??'—';
  $('#lb-sp').textContent=(bb!==null&&ba!==null)?ba-bb:'—';
  $('#lb-mid').textContent=(bb!==null&&ba!==null)?fmtF((bb+ba)/2):'—';
  const imbEl=$('#lb-imb');
  imbEl.textContent=imb!==null?imb.toFixed(2):'—';
  imbEl.className=imb===null?'':(imb>0.6?'pos':imb<0.4?'neg':'');
}
function log(t){$('#lb-log').textContent='» '+t;}

$('#lb-addbid').addEventListener('click',()=>{
  const [p,s]=bidPool[bi++%bidPool.length];
  book.push({id:nextId,side:'buy',price:p,size:s});
  log(`book = add_order(book, make_order('BTCUSDT', 'buy', ${p}, ${s}))   # id=${nextId}`);
  nextId++;render();
});
$('#lb-addask').addEventListener('click',()=>{
  const [p,s]=askPool[ai++%askPool.length];
  book.push({id:nextId,side:'sell',price:p,size:s});
  log(`book = add_order(book, make_order('BTCUSDT', 'sell', ${p}, ${s}))   # id=${nextId}`);
  nextId++;render();
});
$('#lb-cancel').addEventListener('click',()=>{
  if(!book.length){log('no hay nada que cancelar');return;}
  const last=book[book.length-1];
  book=book.filter(o=>o.id!==last.id);
  log(`book = cancel_order(book, order_id=${last.id})   # lista nueva, sin la ${last.id}`);
  render();
});
$('#lb-reset').addEventListener('click',()=>{book=[];nextId=1;bi=0;ai=0;log('book = []');render();});
render();
})();
