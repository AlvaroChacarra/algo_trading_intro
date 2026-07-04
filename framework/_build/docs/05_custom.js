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
  $('#tk-log').textContent=`» tracker.apply_fill(Fill('${side}', ${px}, ${sz}))  →  _cash ${side==='buy'?'−':'+'}${px*sz}, _position ${side==='buy'?'+':'−'}${sz}`;
  render();
}
$('#tk-buy').addEventListener('click',()=>fill('buy'));
$('#tk-sell').addEventListener('click',()=>fill('sell'));
$('#tk-reset').addEventListener('click',()=>{cash=0;pos=0;n=0;
  $('#tk-log').textContent='sin fills — caja y posición a cero';render();});
$('#tk-mark').addEventListener('input',render);
render();
})();
