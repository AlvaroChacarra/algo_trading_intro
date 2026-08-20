/* L6 — polimorfismo vivo: una llamada, tres respuestas */
(function(){
"use strict";
const $=s=>document.querySelector(s);
function decide(strat, imb){
  if(strat==='base')return 'hold';
  if(strat==='momentum')return imb>0.3?'buy':imb<-.3?'sell':'hold';
  /* contraria */
  return imb>0.3?'sell':imb<-.3?'buy':'hold';
}
function paint(id, d){
  const el=$(id);
  el.textContent=`decide(book) → '${d}'`;
  el.className='dec '+d;
}
function update(){
  const imb=(+$('#pf-imb').value)/100;
  $('#pf-imbv').textContent=(imb>0?'+':'')+imb.toFixed(2);
  const ds=['base','momentum','contraria'].map(s=>decide(s,imb));
  paint('#pf-d0',ds[0]);paint('#pf-d1',ds[1]);paint('#pf-d2',ds[2]);
  $('#pf-log').textContent=`» for s in familia: s.decide(book)   # imbalance=${imb.toFixed(2)} → ${ds.join(' · ')}`;
}
$('#pf-imb').addEventListener('input',update);
update();

/* super(): herencia automática, constructor reemplazado y cooperación explícita */
(function(){
  const modes={
    'sup-a':{
      code:"class Umbral(Strategy):\n    pass\n\nu = Umbral('u1')",
      trace:['Umbral no define __init__','Python usa Strategy.__init__','name = "u1"'],
      state:[['name','"u1"']],status:'completo ✓'},
    'sup-b':{
      code:"class Umbral(Strategy):\n    def __init__(self, threshold):\n        self.threshold = threshold\n\nu = Umbral(0.6)",
      trace:['Umbral define su __init__','Strategy.__init__ no se ejecuta','threshold = 0.6'],
      state:[['name','??? ✗'],['threshold','0.6']],status:'falta name ✗'},
    'sup-c':{
      code:"class Umbral(Strategy):\n    def __init__(self, name, threshold):\n        super().__init__(name)\n        self.threshold = threshold\n\nu = Umbral('u1', 0.6)",
      trace:['Strategy.__init__ → name = "u1"','vuelve al mismo objeto u','Umbral.__init__ → threshold = 0.6'],
      state:[['name','"u1"'],['threshold','0.6']],status:'completo ✓'},
  };
  function show(id){
    Object.keys(modes).forEach(x=>$('#'+x).classList.toggle('on',x===id));
    const m=modes[id];$('#sup-code').textContent=m.code;
    $('#sup-trace').innerHTML=m.trace.map((x,i)=>`<div class="trace-step ${id==='sup-b'&&i===1?'fail':'ok'}"><span>${x}</span></div>`).join('');
    $('#sup-state').innerHTML=m.state.map(([k,v])=>`<div><span>${k}</span><b>${v}</b></div>`).join('');
    $('#sup-status').textContent=m.status;$('#sup-status').style.color=id==='sup-b'?'var(--ask)':'var(--bid)';
  }
  Object.keys(modes).forEach(id=>$('#'+id).addEventListener('click',()=>show(id)));
  show('sup-a');
})();

/* ABC: el cuerpo y el contrato son dimensiones distintas */
(function(){
  const modes={
    'abc-default':{
      code:"class Strategy:\n    def decide(self, book):\n        return 'hold'\n\nclass Incompleta(Strategy):\n    pass",
      trace:[['Incompleta()','ok'],['decide() → "hold"','ok']],
      log:'objeto creado ✓ · hereda comportamiento por defecto'},
    'abc-abstract':{
      code:"class Strategy(ABC):\n    @abstractmethod\n    def decide(self, book):\n        ...\n\nclass Incompleta(Strategy):\n    pass",
      trace:[['Incompleta()','fail'],['TypeError · falta decide','fail']],
      log:'objeto no creado: el contrato obliga a implementar'},
    'abc-return':{
      code:"class Strategy(ABC):\n    @abstractmethod\n    def decide(self, book):\n        return 'hold'\n\nclass Incompleta(Strategy):\n    pass",
      trace:[['el método tiene cuerpo','ok'],['Incompleta()','fail'],['TypeError · sigue abstracto','fail']],
      log:'return aporta comportamiento; el decorador mantiene el contrato'},
  };
  function show(id){
    Object.keys(modes).forEach(x=>$('#'+x).classList.toggle('on',x===id));
    const m=modes[id];$('#abc-code').textContent=m.code;
    $('#abc-trace').innerHTML=m.trace.map(([x,cls])=>`<div class="trace-step ${cls}"><span>${x}</span></div>`).join('');
    $('#abc-log').textContent=m.log;
  }
  Object.keys(modes).forEach(id=>$('#'+id).addEventListener('click',()=>show(id)));
  show('abc-default');
})();
})();
