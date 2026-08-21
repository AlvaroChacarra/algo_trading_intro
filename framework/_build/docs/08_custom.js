/* L8 — execution trace y simulador derivados del MatchingEngine canónico. */
(function(){
"use strict";
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],D=DOC_DATA;
const rows=xs=>xs.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
function bookHTML(book,focus){return book.asks.slice().reverse().map(x=>`<div class="row a" style="${focus==='asks'?'background:rgba(248,113,113,.08)':''}"><span>ask ${x[0]}</span><small>${(+x[1]).toFixed(3)}</small></div>`).join('')+'<div class="sep"></div>'+book.bids.map(x=>`<div class="row b" style="${focus==='bids'?'background:rgba(74,222,128,.08)':''}"><span>bid ${x[0]}</span><small>${(+x[1]).toFixed(3)}</small></div>`).join('');}
const base={bids:D.bids,asks:D.asks};

const codeStages=[
`class MatchingEngine:
<span class="active-line">    def process(self, order, book, timestamp=None):</span>
        # Construiremos este contrato.
        ...`,
`class MatchingEngine:
    def process(self, order, book, timestamp=None):
<span class="active-line">        opposite = (book.asks</span>
<span class="active-line">            if order.side is Side.BUY else book.bids)</span>`,
`class MatchingEngine:
    def process(self, order, book, timestamp=None):
        opposite = book.asks if order.side is Side.BUY else book.bids
<span class="active-line">        remaining = order.size</span>`,
`class MatchingEngine:
    def process(self, order, book, timestamp=None):
        opposite = book.asks if order.side is Side.BUY else book.bids
        remaining = order.size
        for level in opposite:
            if remaining &lt;= _EPS: break
<span class="active-line">            take = min(remaining, level.size)</span>`,
`# PROPUESTA INGENUA — incorrecta para FOK
def process(self, order, book, timestamp=None):
    opposite = book.asks if order.side is Side.BUY else book.bids
    remaining = order.size
    for level in opposite:
        take = min(remaining, level.size)
<span class="active-line">        book.reduce(order.side.opposite,</span>
<span class="active-line">                    level.price, take)</span>
        remaining -= take
    if order.order_type is OrderType.FOK and remaining &gt; _EPS:
<span class="active-line">        return []  # demasiado tarde</span>`,
`def process(self, order, book, timestamp=None):
    opposite = book.asks if order.side is Side.BUY else book.bids
    remaining = order.size
<span class="active-line">    planned = []</span>
    for level in opposite:
        if remaining &lt;= _EPS: break
        take = min(remaining, level.size)
<span class="active-line">        planned.append((level.price, take))</span>
        remaining -= take
    # book todavía intacto`,
`def process(self, order, book, timestamp=None):
    opposite = book.asks if order.side is Side.BUY else book.bids
    remaining = order.size
    planned = []
    for level in opposite:
        if remaining &lt;= _EPS: break
        take = min(remaining, level.size)
        planned.append((level.price, take))
        remaining -= take
<span class="active-line">    filled = order.size - remaining</span>
<span class="active-line">    if (order.order_type is OrderType.FOK</span>
<span class="active-line">            and filled &lt; order.size - _EPS):</span>
<span class="active-line">        return []</span>`,
`def process(self, order, book, timestamp=None):
    ...  # SELECT + PLAN + VALIDATE
<span class="active-line">    fills = []</span>
<span class="active-line">    for price, take in planned:</span>
<span class="active-line">        book.reduce(order.side.opposite, price, take)</span>
<span class="active-line">        fills.append(Fill(order.id, order.symbol,</span>
<span class="active-line">                          order.side, price, take, timestamp))</span>`,
`def process(self, order, book, timestamp=None):
    ...  # SELECT + PLAN + VALIDATE + COMMIT
<span class="active-line">    if (remaining &gt; _EPS</span>
<span class="active-line">            and order.order_type is OrderType.LIMIT):</span>
<span class="active-line">        book.add_limit(order.side, order.price, remaining)</span>
<span class="active-line">    return fills</span>`
];
function paintBuildCode(stage){$('#l8-build-code').innerHTML=codeStages[stage];}
$('#l8-build-fig').addEventListener('stagechange',e=>paintBuildCode(e.detail.stage));paintBuildCode(0);

function paintTraceSide(side){$('#trace-side-book').innerHTML=bookHTML(base,side==='buy'?'asks':'bids');}
$$('#trace-side button').forEach(b=>b.addEventListener('click',()=>{$$('#trace-side button').forEach(x=>x.classList.toggle('on',x===b));paintTraceSide(b.dataset.side);}));paintTraceSide('buy');
const hero=D.scenarios.find(x=>x.key==='buy:market:1:-1');
$('#trace-size').textContent=hero.size;$('#trace-rem0').textContent=hero.size;
const first=hero.planned[0],rem1=hero.size-first[1];
$('#trace-take').innerHTML=rows([['remaining',hero.size],['level.size',first[1]],['take = min(...)',first[1]]]);
$('#trace-after-take').innerHTML=rows([['remaining antes',hero.size],['take',`− ${first[1]}`],['remaining después',rem1.toFixed(3)]]);
$('#trace-plan').innerHTML=D.fokBug.planned.map((x,i)=>`<div class="trace-step ${i===D.fokBug.planned.length-1?'active':'ok'}"><span>(${x[0]}, ${x[1].toFixed(3)})</span><span class="trace-meta">nivel ${i+1}</span></div>`).join('');
$('#trace-commit-book').innerHTML=bookHTML(hero.after);$('#trace-fill').textContent=`Fill(price=${first[0]}, size=${first[1].toFixed(3)})`;
$('#trace-rest').textContent=hero.remaining.toFixed(3);

const bug=D.fokBug,plannedTotal=bug.planned.reduce((s,x)=>s+x[1],0);
$('#fok-bug-summary').innerHTML=rows([['order.size',bug.size.toFixed(3)],['plan llena',plannedTotal.toFixed(3)],['falta',bug.remaining.toFixed(3)]]);
const sizeAt=(book,side,price)=>{const lv=book[side].find(x=>x[0]===price);return lv?+lv[1]:0;};
$('#fok-bug-diff').innerHTML=rows(bug.planned.map(([price])=>[
  `ask ${price}`,
  `${sizeAt(bug.before,'asks',price).toFixed(3)} → ${sizeAt(bug.naiveAfter,'asks',price).toFixed(3)}`
]).concat([['fills devueltos','[]'],['book','YA CAMBIÓ 💥']]));

const policy={
 market:[['SELECT','opposite'],['LOOP','sin límite de precio'],['VALIDATE','no aplica'],['COMMIT','reduce + Fill'],['REMAINING','descartar']],
 limit:[['SELECT','opposite'],['LOOP','_crosses(order, price)'],['VALIDATE','no aplica'],['COMMIT','reduce + Fill'],['REMAINING','add_limit']],
 ioc:[['SELECT','opposite'],['LOOP','igual que LIMIT'],['VALIDATE','no aplica'],['COMMIT','reduce + Fill'],['REMAINING','descartar']],
 fok:[['SELECT','opposite'],['LOOP','_crosses(order, price)'],['VALIDATE','todo o return []'],['COMMIT','solo si completa'],['REMAINING','nunca descansa']]
};
const notes={market:'Cruza mientras exista liquidez. Nada descansa.',limit:'La única política que añade el remanente al book.',ioc:'Mismo plan y commit que LIMIT; sin add_limit.',fok:'Si no completa, return [] antes del primer reduce.'};
function paintPolicy(mode){$('#policy-trace').innerHTML=policy[mode].map((x,i)=>`<div class="branch-row ${i===policy[mode].length-1?'on':''}"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');$('#policy-note').innerHTML=`<span class="tag">${mode.toUpperCase()}</span>${notes[mode]}`;}
$$('#policy-modes button').forEach(b=>b.addEventListener('click',()=>{$$('#policy-modes button').forEach(x=>x.classList.toggle('on',x===b));paintPolicy(b.dataset.mode);}));paintPolicy('market');

function paintCrosses(side){
  const prices=D.limitPrices[side],limit=prices[1],isBuy=side==='buy';
  $('#cross-limit').textContent=`limit = ${limit}`;
  $('#cross-code').innerHTML=isBuy
    ? '<span class="ln">if order.side is Side.BUY:</span><span class="ln hl">    return order.price &gt;= level_price</span><span class="ln">return order.price &lt;= level_price</span>'
    : '<span class="ln">if order.side is Side.BUY:</span><span class="ln">    return order.price &gt;= level_price</span><span class="ln hl">return order.price &lt;= level_price</span>';
  $('#cross-levels').innerHTML=rows(prices.map(price=>{
    const crosses=isBuy?limit>=price:limit<=price;
    return [`${isBuy?'ask':'bid'} ${price}`,crosses?'✓ cruza':'✗ STOP'];
  }));
}
$$('#cross-side button').forEach(b=>b.addEventListener('click',()=>{$$('#cross-side button').forEach(x=>x.classList.toggle('on',x===b));paintCrosses(b.dataset.side);}));paintCrosses('buy');

let sim={type:'market',side:'buy',sizeI:1,priceI:1,phase:0};
function scenario(){const pi=sim.type==='market'?-1:sim.priceI;return D.scenarios.find(x=>x.key===`${sim.side}:${sim.type}:${sim.sizeI}:${pi}`);}
function resetPhase(){sim.phase=0;paintSim();}
function paintSim(){const s=scenario();$('#sim-size-v').textContent=s.size;$('#sim-price-row').style.display=sim.type==='market'?'none':'flex';$('#sim-price-v').textContent=s.price??'MKT';
  const phases=[['1 · SELECT','lado contrario'],['2 · PLAN',`${s.planned.length} niveles`],['3 · VALIDATE',sim.type==='fok'?(s.fills.length?'FOK completa':'FOK aborta'):'ok'],['4 · COMMIT',`${s.fills.length} fills`]];
  $('#sim-phases').innerHTML=phases.map((x,i)=>`<div class="trace-step ${i<sim.phase?'ok':i===sim.phase?'active':''}"><span>${x[0]}</span><span class="trace-meta">${x[1]}</span></div>`).join('');
  const committed=sim.phase>=3;$('#sim-book-label').textContent=committed?'after':'before';$('#sim-book').innerHTML=bookHTML(committed?s.after:s.before,sim.phase===0?(sim.side==='buy'?'asks':'bids'):null);
  let detail=[];if(sim.phase===0)detail=[['opposite',sim.side==='buy'?'asks':'bids'],['remaining',s.size]];
  if(sim.phase===1)detail=s.planned.map((x,i)=>[`planned[${i}]`,`${x[1].toFixed(3)} @ ${x[0]}`]).concat([['remaining',s.remaining.toFixed(3)]]);
  if(sim.phase===2)detail=[['policy',sim.type.toUpperCase()],['valid',sim.type==='fok'?(s.fills.length?'sí':'NO → return []'):'sí']];
  if(sim.phase>=3){
    detail=s.fills.map((x,i)=>[`Fill ${i+1}`,`${x[1].toFixed(3)} @ ${x[0]}`]);
    if(s.remaining>1e-9&&sim.type==='limit')detail.push(['remanente',`${s.remaining.toFixed(3)} descansa @ ${s.price}`]);
    if(s.remaining>1e-9&&['market','ioc'].includes(sim.type))detail.push(['remanente',`${s.remaining.toFixed(3)} cancelado`]);
  }
  if(sim.phase>=3&&!s.fills.length)detail=[['fills','[]'],['book','idéntico']];$('#sim-detail').innerHTML=rows(detail);
}
$$('#sim-type button').forEach(b=>b.addEventListener('click',()=>{$$('#sim-type button').forEach(x=>x.classList.toggle('on',x===b));sim.type=b.dataset.type;resetPhase();}));
$$('#sim-side button').forEach(b=>b.addEventListener('click',()=>{$$('#sim-side button').forEach(x=>x.classList.toggle('on',x===b));sim.side=b.dataset.side;resetPhase();}));
$('#sim-size').addEventListener('input',e=>{sim.sizeI=+e.target.value;resetPhase();});$('#sim-price').addEventListener('input',e=>{sim.priceI=+e.target.value;resetPhase();});
$('#sim-next').addEventListener('click',()=>{sim.phase=Math.min(3,sim.phase+1);paintSim();});$('#sim-reset').addEventListener('click',resetPhase);paintSim();
})();
