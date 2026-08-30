/* L9 — anatomía de Market y reproducción del loop canónico. */
(function(){
"use strict";
const $=s=>document.querySelector(s),D=DOC_DATA,A=D.anatomy,E=D.equity,F=D.fills[0];
const rows=xs=>xs.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
const codeStages=[
`class Market:
    def __init__(self, symbol, snapshots, depth=10):
        self.symbol = symbol
        self._snapshots = snapshots
        self._depth = depth
        self._engine = MatchingEngine()
        self._i = -1
        self._timestamp = None
        self.book = None

    def step(self):
<span class="active-line">        next_i = self._i + 1</span>
        # El estado observable aun no cambia.`,
`class Market:
    ...

    def step(self):
        next_i = self._i + 1
        snapshot = self._snapshots[next_i]
<span class="active-line">        next_book = OrderBook.from_snapshot(</span>
<span class="active-line">            self.symbol, snapshot, self._depth)</span>
        raw_timestamp = snapshot.get("timestamp", next_i)
<span class="active-line">        next_timestamp = _integer_timestamp(raw_timestamp)</span>
        # Si algo falla arriba, _i/_timestamp/book no cambian.`,
`class Market:
    ...

    def step(self):
        next_i = self._i + 1
        if next_i &gt;= len(self._snapshots):
<span class="active-line">            self._i = next_i</span>
<span class="active-line">            self._timestamp = None</span>
<span class="active-line">            self.book = None</span>
            return None

        snapshot = self._snapshots[next_i]
        next_book = OrderBook.from_snapshot(
            self.symbol, snapshot, self._depth)
        raw_timestamp = snapshot.get("timestamp", next_i)
        next_timestamp = _integer_timestamp(raw_timestamp)

<span class="active-line">        self._i = next_i</span>
<span class="active-line">        self._timestamp = next_timestamp</span>
<span class="active-line">        self.book = next_book</span>
<span class="active-line">        return next_book</span>`,
`class Market:
    ...

    @property
<span class="active-line">    def timestamp(self):</span>
<span class="active-line">        return self._timestamp</span>

    def step(self):
        ...`,
`class Market:
    ...

    @property
    def timestamp(self): ...

    def step(self): ...

<span class="active-line">    def submit(self, order):</span>
<span class="active-line">        if self.book is None:</span>
<span class="active-line">            raise RuntimeError("llama a step() primero")</span>
<span class="active-line">        return self._engine.process(</span>
<span class="active-line">            order, self.book, self.timestamp)</span>`,
`class Market:
    def __init__(self, symbol, snapshots, depth=10):
        self._snapshots = snapshots
<span class="active-line">        self._engine = MatchingEngine()</span>
        self._i = -1
        self._timestamp = None
        self.book = None
    ...
    def submit(self, order):
        if self.book is None:
            raise RuntimeError(...)
<span class="active-line">        return self._engine.process(</span>
<span class="active-line">            order, self.book, self.timestamp)</span>`,
`class Market:
    def __init__(self, symbol, snapshots, depth=10):
        self._snapshots = snapshots
        self._engine = MatchingEngine()
        self._i = -1
        self._timestamp = None
        self.book = None
    ...
    def submit(self, order): ...

<span class="active-line">    def reset(self):</span>
<span class="active-line">        self._i = -1</span>
<span class="active-line">        self._timestamp = None</span>
<span class="active-line">        self.book = None</span>`
];
function paintBuildCode(stage){$('#l9-build-code').innerHTML=codeStages[stage];}
$('#l9-build-fig').addEventListener('stagechange',e=>paintBuildCode(e.detail.stage));paintBuildCode(0);
function snapTrace(i){return A.map((x,k)=>`<div class="trace-step ${k===i?'active':k<i?'ok':''}"><span>[${k}] ${x.timestamp}</span><span class="trace-meta">mid ${x.mid}</span></div>`).join('');}
function paintInspector(i){$('#mk-i-v').textContent=i;$('#mk-snaps').innerHTML=snapTrace(i);const active=i>=0?A[i]:null;$('#mk-state').innerHTML=rows([['_i',i],['book',active?`OrderBook(${active.bestBid} / ${active.bestAsk})`:'None'],['_engine','MatchingEngine()'],['_depth',10]]);}
$('#mk-i').addEventListener('input',e=>paintInspector(+e.target.value));paintInspector(-1);
$('#mk-step-book').innerHTML=`<div class="row a"><span>ask ${A[0].bestAsk}</span><small>best ask</small></div><div class="sep"></div><div class="row b"><span>bid ${A[0].bestBid}</span><small>best bid</small></div>`;
$('#mk-ts-value').textContent=A[0].timestamp;

let timer=null;const mark={i:F.i,v:E[F.i]};
const owner=i=>`<div class="trace-step ${i>0?'ok':'active'}"><span>Market.step()</span><span class="trace-meta">_i + book</span></div>`+(i>F.i?`<div class="trace-step ok"><span>Market.submit()</span><span class="trace-meta">delega L8</span></div><div class="trace-step ok"><span>PositionTracker</span><span class="trace-meta">equity</span></div>`:'<div class="trace-step"><span>sin orden</span><span class="trace-meta">solo tiempo</span></div>');
function stop(){if(timer)clearInterval(timer);timer=null;}
$('#pl-play').addEventListener('click',()=>{stop();let i=2;$('#pl-play').disabled=true;timer=setInterval(()=>{i=Math.min(E.length,i+5);DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:i,endDot:true}],{zero:true,marks:i>F.i?[mark]:[]});$('#pl-log').textContent=`paso ${i}/${E.length} · equity ${E[i-1]}`;$('#pl-owner').innerHTML=owner(i);if(i>=E.length){stop();$('#pl-play').disabled=false;$('#pl-log').textContent=`día completo · equity final ${D.finalEquity}`;}},30);});
$('#pl-reset').addEventListener('click',()=>{stop();$('#pl-play').disabled=false;DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:2}]);$('#pl-log').textContent='pulsa play';$('#pl-owner').innerHTML=owner(0);});
DOC.chart('#pl-chart',[{data:E,color:'#22d3ee',upTo:2}]);$('#pl-owner').innerHTML=owner(0);
})();
