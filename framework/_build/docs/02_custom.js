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
  return (b+a)>0?(b-a)/(b+a):null;
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
  imbEl.textContent=imb!==null?(imb>0?'+':'')+imb.toFixed(2):'—';
  imbEl.className=imb===null?'':(imb>0.2?'pos':imb<-.2?'neg':'');
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

/* cancel_order: primero la traza explícita, después la comprehension */
(function(){
  const source=[{id:1,side:'buy',price:99950},{id:2,side:'sell',price:100000}];
  let i=0,result=[],compact=false;
  const row=o=>`<div class="row ${o.side==='buy'?'b':'a'}"><span>id=${o.id} · ${o.side}</span><small>${o.price}</small></div>`;
  function code(){
    $('#cancel-code').textContent=compact
      ?"new_book = [o for o in book if o['id'] != order_id]"
      :"new_book = []\nfor o in book:\n    if o['id'] != order_id:\n        new_book.append(o)";
  }
  function renderCancel(){
    $('#cancel-source').innerHTML=source.map(row).join('');
    $('#cancel-result').innerHTML=result.length?result.map(row).join(''):'<span style="color:var(--faint)">— vacía —</span>';
    $('#cancel-count').textContent=`${result.length} orden${result.length===1?'':'es'}`;
    code();
  }
  function reset(){i=0;result=[];$('#cancel-next').textContent='▶ siguiente orden';$('#cancel-trace').innerHTML='';
    $('#cancel-log').textContent='book is new_book → aún no calculado';renderCancel();}
  $('#cancel-next').addEventListener('click',()=>{
    if(i>=source.length){reset();return;}
    const o=source[i],keep=o.id!==1;
    if(keep)result.push(o);
    $('#cancel-trace').insertAdjacentHTML('beforeend',
      `<div class="trace-step ${keep?'ok':'fail'}"><span>id=${o.id}: ${o.id} != 1 → ${keep?'TRUE':'FALSE'}</span><span class="trace-meta">${keep?'pasa':'se descarta'}</span></div>`);
    i++;renderCancel();
    if(i===source.length){
      $('#cancel-log').textContent='book → 2 · new_book → 1 · book is new_book → False';
      $('#cancel-next').textContent='↻ otra vez';
    }else $('#cancel-log').textContent='la lista original sigue teniendo 2 órdenes';
  });
  $('#cancel-reset').addEventListener('click',()=>{$('#cancel-next').textContent='▶ siguiente orden';reset();});
  $('#cancel-explicit').addEventListener('click',()=>{compact=false;$('#cancel-explicit').classList.add('on');$('#cancel-comp').classList.remove('on');code();});
  $('#cancel-comp').addEventListener('click',()=>{compact=true;$('#cancel-comp').classList.add('on');$('#cancel-explicit').classList.remove('on');code();});
  reset();
})();

/* sorted(key=...): la función es un valor que sorted llama por cada orden */
(function(){
  const orders=[{name:'A',price:105},{name:'B',price:100},{name:'C',price:110}];
  let i=0,useLambda=false;
  function paintCode(){
    $('#sort-code').textContent=useLambda
      ?"sorted(orders, key=lambda order: order['price'])"
      :"def get_price(order):\n    return order['price']\n\nsorted(orders, key=get_price)";
  }
  function resetSort(){i=0;$('#sort-trace').innerHTML='';$('#sort-next').textContent='▶ siguiente orden';
    $('#sort-log').textContent='La función se pasa sin paréntesis: sorted la llamará.';paintCode();}
  $('#sort-next').addEventListener('click',()=>{
    if(i>=orders.length){resetSort();return;}
    const o=orders[i++],fn=useLambda?'lambda(order)':`get_price(${o.name})`;
    $('#sort-trace').insertAdjacentHTML('beforeend',`<div class="trace-step ok"><span>order ${o.name} → ${fn}</span><span class="trace-meta">${o.price}</span></div>`);
    if(i===orders.length){$('#sort-log').textContent='claves 105 · 100 · 110 → orden final B · A · C';$('#sort-next').textContent='↻ otra vez';}
  });
  $('#sort-fn').addEventListener('click',()=>{useLambda=false;$('#sort-fn').classList.add('on');$('#sort-lambda').classList.remove('on');resetSort();});
  $('#sort-lambda').addEventListener('click',()=>{useLambda=true;$('#sort-lambda').classList.add('on');$('#sort-fn').classList.remove('on');resetSort();});
  resetSort();
})();
})();
