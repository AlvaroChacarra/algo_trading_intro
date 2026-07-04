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
})();
