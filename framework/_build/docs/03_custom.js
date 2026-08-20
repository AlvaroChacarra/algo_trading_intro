/* L3 — simulador del espacio de nombres según el estilo de import */
(function(){
"use strict";
const $=s=>document.querySelector(s);
const modo={
  'imp-a':`<span class="k">import</span> order_book

<span class="c"># nombres disponibles en main.py:</span>
<span style="color:var(--num)">order_book</span>                <span class="c">← el módulo entero</span>
order_book.make_order(…)
order_book.best_bid(book)
order_book.imbalance(book)</span>`,
  'imp-b':`<span class="k">from</span> order_book <span class="k">import</span> imbalance

<span class="c"># nombres disponibles en main.py:</span>
<span style="color:var(--num)">imbalance</span>                 <span class="c">← solo este</span>
imbalance(book)           <span class="c"># sin prefijo</span>
<span style="color:var(--ask)">order_book.best_bid(…)    # NameError</span>`,
  'imp-c':`<span class="k">import</span> order_book <span class="k">as</span> ob

<span class="c"># nombres disponibles en main.py:</span>
<span style="color:var(--num)">ob</span>                        <span class="c">← alias corto</span>
ob.best_bid(book)
ob.imbalance(book)        <span class="c"># mismo módulo, menos letras</span>`,
};
['imp-a','imp-b','imp-c'].forEach(id=>{
  $('#'+id).addEventListener('click',()=>{
    ['imp-a','imp-b','imp-c'].forEach(x=>$('#'+x).classList.toggle('on',x===id));
    $('#imp-out').innerHTML=modo[id];
  });
});
$('#imp-out').innerHTML=modo['imp-a'];

/* importar vs ejecutar: el guard resuelve un side effect observable */
(function(){
  let guarded=false,direct=false;
  const code=()=>guarded
    ?`def run_backtest():\n    ...\n\ndef main():\n    print("ARRANCANDO BACKTEST")\n    run_backtest()\n\nif __name__ == "__main__":\n    main()`
    :`def run_backtest():\n    ...\n\nprint("ARRANCANDO BACKTEST")\nrun_backtest()`;
  function choose(id,on){$(id).classList.toggle('on',on);}
  function renderMain(){
    choose('#main-broken',!guarded);choose('#main-fixed',guarded);
    choose('#main-import',!direct);choose('#main-direct',direct);
    $('#main-code').textContent=code();$('#main-trace').innerHTML='';
  }
  $('#main-broken').addEventListener('click',()=>{guarded=false;renderMain();});
  $('#main-fixed').addEventListener('click',()=>{guarded=true;renderMain();});
  $('#main-import').addEventListener('click',()=>{direct=false;renderMain();});
  $('#main-direct').addEventListener('click',()=>{direct=true;renderMain();});
  $('#main-run').addEventListener('click',()=>{
    const name=direct?'__main__':'backtest';
    const steps=[['Python entra en backtest.py','ok'],['define run_backtest ✓','ok']];
    if(guarded){
      steps.push([`__name__ = "${name}"`,'ok'],[`condición → ${direct?'TRUE':'FALSE'}`,'ok']);
      if(direct)steps.push(['main() → ARRANCANDO BACKTEST','ok']);
    }else{
      steps.push(['print("ARRANCANDO BACKTEST")','fail'],['run_backtest()','fail']);
    }
    $('#main-trace').innerHTML=steps.map(([label,cls])=>`<div class="trace-step ${cls}"><span>${label}</span></div>`).join('');
    $('#main-log').textContent=!guarded&&!direct?'⚠ el import ha lanzado el backtest'
      :guarded&&!direct?'✓ import limpio: define funciones y no arranca'
      :'✓ ejecución directa: el programa arranca de forma intencional';
  });
  renderMain();
})();
})();
