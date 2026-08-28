/* L5 — el PositionTracker vivo: fills por la puerta, equity al instante */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const BID=99950, ASK=100010;
let cash=0, pos=0, n=0;
function fmt(x){const r=Math.round(x*100)/100;return (r>0?'+':'')+(Number.isInteger(r)?r+'.0':r);}
function render(){
  const mark=+$('#tk-mark').value;
  $('#tk-markv').textContent=mark;
  const eq=cash+pos*mark;
  const set=(id,v,signed)=>{const el=$(id);el.textContent=signed?fmt(v):String(Math.round(v*100)/100);
    el.className=v>1e-9?'pos':v<-1e-9?'neg':'';};
  set('#tk-cash',cash,true);
  $('#tk-pos').textContent=String(Math.round(pos*100)/100);
  $('#tk-pos').className=pos>1e-9?'pos':pos<-1e-9?'neg':'';
  set('#tk-eq',eq,true);
  $('#tk-n').textContent=n;
}
function fill(side){
  const px=side==='buy'?ASK:BID, sz=0.5;
  cash+=side==='buy'?-px*sz:px*sz;
  pos+=side==='buy'?sz:-sz;
  n++;
  $('#tk-log').textContent=`» tracker.apply_fill(Fill(1, 'BTCUSDT', '${side}', ${px}, ${sz}))  →  _cash ${side==='buy'?'−':'+'}${px*sz}, _position ${side==='buy'?'+':'−'}${sz}`;
  render();
}
$('#tk-buy').addEventListener('click',()=>fill('buy'));
$('#tk-sell').addEventListener('click',()=>fill('sell'));
$('#tk-reset').addEventListener('click',()=>{cash=0;pos=0;n=0;
  $('#tk-log').textContent='sin fills — caja y posición a cero';render();});
$('#tk-mark').addEventListener('input',render);
render();

/* la convención mantiene el invariante; tocar un atributo interno lo invalida */
(function(){
  let invCash=0,invPos=0,broken=false;
  function invRender(){
    $('#inv-cash').textContent=invCash.toLocaleString('en-US');
    $('#inv-pos').textContent=String(invPos);
    $('#inv-status').textContent=broken?'consistente ✗':'consistente ✓';
    $('#inv-status').style.color=broken?'var(--ask)':'var(--bid)';
    $('#inv-state').classList.toggle('bad',broken);
    $('#inv-state').classList.toggle('changed',!broken);
  }
  $('#inv-fill').addEventListener('click',()=>{
    invCash=-50000;invPos=.5;broken=false;
    $('#inv-log').textContent="apply_fill(buy) → cash −50000 y position +0.5 · juntas";invRender();
  });
  $('#inv-break').addEventListener('click',()=>{
    invCash=1000000;broken=true;
    $('#inv-log').textContent='tracker._cash = 1_000_000 funciona; la clase ya no puede garantizar su estado';invRender();
  });
  $('#inv-reset').addEventListener('click',()=>{
    invCash=0;invPos=0;broken=false;$('#inv-log').textContent='El objeto controla su estado mientras entras por su API.';invRender();
  });
  invRender();
})();
})();
