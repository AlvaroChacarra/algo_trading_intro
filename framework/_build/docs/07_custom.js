/* L7 — raw snapshot → Level → OrderBook; el scrubber conserva los 500 reales. */
(function(){
"use strict";
const $=s=>document.querySelector(s),D=DOC_DATA,S=D.snaps,R=D.raw;
const stateRows=rows=>rows.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
function bookHTML(s){return s.asks.slice().reverse().map(x=>`<div class="row a"><span>ask ${x[0]}</span><small>${x[1].toFixed(3)}</small></div>`).join('')+'<div class="sep"></div>'+s.bids.map(x=>`<div class="row b"><span>bid ${x[0]}</span><small>${x[1].toFixed(3)}</small></div>`).join('');}

const codeStages=[
`# Todavía solo existe una fila externa:
row["bid_price_1"]
row["bid_size_1"]`,
`from dataclasses import dataclass

<span class="active-line">@dataclass</span>
<span class="active-line">class Level:</span>
    price: float
    size: float`,
`@dataclass
class Level:
    price: float
    size: float

class OrderBook:
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
<span class="active-line">        self.bids = bids</span>
<span class="active-line">        self.asks = asks</span>`,
`@dataclass
class Level:
    price: float
    size: float

class OrderBook:
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
<span class="active-line">        self.bids = sorted(</span>
            bids, key=lambda lv: -lv.price)
<span class="active-line">        self.asks = sorted(</span>
            asks, key=lambda lv: lv.price)`,
`class OrderBook:
<span class="active-line">    def __init__(self, symbol, bids, asks):</span>
        self.symbol = symbol
        self.bids = sorted(
            bids, key=lambda lv: -lv.price)
        self.asks = sorted(
            asks, key=lambda lv: lv.price)

# Las dos entradas terminan en __init__.`,
`class OrderBook:
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

<span class="active-line">    @classmethod</span>
<span class="active-line">    def from_snapshot(cls, symbol, row, depth=10):</span>
        bids, asks = [], []
        for i in range(1, depth + 1):
            bp = row.get(f"bid_price_{i}")
            bs = row.get(f"bid_size_{i}")
            ap = row.get(f"ask_price_{i}")
            az = row.get(f"ask_size_{i}")
            if bp is not None and bs is not None and float(bs) &gt; 0:
                bids.append(Level(float(bp), float(bs)))
            if ap is not None and az is not None and float(az) &gt; 0:
                asks.append(Level(float(ap), float(az)))
<span class="active-line">        return cls(symbol, bids, asks)</span>`,
`class OrderBook:
    def __init__(self, symbol, bids, asks):
        self.symbol = symbol
        self.bids = sorted(bids, key=lambda lv: -lv.price)
        self.asks = sorted(asks, key=lambda lv: lv.price)

    @classmethod
    def from_snapshot(cls, symbol, row, depth=10):
        ...
        return cls(symbol, bids, asks)

<span class="active-line">    def depth(self, side, levels=10): ...</span>
<span class="active-line">    def imbalance(self, levels=1): ...</span>
<span class="active-line">    @property</span>
<span class="active-line">    def microprice(self): ...</span>`
];
function paintCode(stage){$('#l7-build-code').innerHTML=codeStages[stage];}
$('#l7-build-fig').addEventListener('stagechange',e=>paintCode(e.detail.stage));
paintCode(0);

$('#l7-raw').innerHTML=stateRows(R.flatMap(x=>[[`bid_price_${x.i}`,x.bidPrice],[`bid_size_${x.i}`,x.bidSize],[`ask_price_${x.i}`,x.askPrice],[`ask_size_${x.i}`,x.askSize]]));
$('#l7-before-level').textContent=`price=${R[0].bidPrice}, size=${R[0].bidSize}`;
$('#l7-after-level').textContent=`Level(price=${R[0].bidPrice}, size=${R[0].bidSize})`;
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
