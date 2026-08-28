/* L4 — taller de órdenes: OrderMini(symbol, side, price, size) en vivo */
(function(){
"use strict";
const $=s=>document.querySelector(s);
let side='buy';
function fmtF(x){return Number.isInteger(x)?x+'.0':String(Math.round(x*100000000)/100000000);}
function update(){
  const price=parseFloat($('#ow-price').value)||0;
  const size=parseFloat($('#ow-size').value)||0;
  const notional=price*size;
  const cf=side==='buy'?-notional:notional;
  $('#ow-repr').textContent=`OrderMini(${side} ${size} BTCUSDT @ ${price})`;
  $('#ow-not').textContent=fmtF(notional);
  const cfEl=$('#ow-cf');
  cfEl.textContent=(cf>0?'+':'')+fmtF(cf);
  cfEl.className=cf>0?'pos':cf<0?'neg':'';
  $('#ow-log').textContent=`» order = OrderMini('BTCUSDT', '${side}', ${price}, ${size})  ·  order.notional() = ${fmtF(notional)}  ·  FillMini('BTCUSDT', '${side}', ${price}, ${size}).cash_flow() = ${fmtF(cf)}`;
}
$('#ow-buy').addEventListener('click',()=>{side='buy';$('#ow-buy').classList.add('on');$('#ow-sell').classList.remove('on');update();});
$('#ow-sell').addEventListener('click',()=>{side='sell';$('#ow-sell').classList.add('on');$('#ow-buy').classList.remove('on');update();});
$('#ow-price').addEventListener('input',update);
$('#ow-size').addEventListener('input',update);
update();
})();
