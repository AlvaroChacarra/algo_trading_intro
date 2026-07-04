
(function(){
"use strict";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── hero order book ─────────────────────────── */
(function(){
  const asks=[{px:100050,sz:1.2},{px:100025,sz:0.8},{px:100000,sz:1.6}];
  const bids=[{px:99950,sz:2.1},{px:99925,sz:0.9},{px:99900,sz:1.4}];
  const A=$('#asks'),B=$('#bids');
  function render(){
    const mx=Math.max(...asks.concat(bids).map(l=>l.sz));
    A.innerHTML=asks.map(l=>`<div class="lvl a"><span class="px">${l.px.toLocaleString('en-US')}</span><span class="bar" style="width:${l.sz/mx*100}%"></span><span class="sz">${l.sz.toFixed(2)}</span></div>`).join('');
    B.innerHTML=bids.map(l=>`<div class="lvl b"><span class="px">${l.px.toLocaleString('en-US')}</span><span class="bar" style="width:${l.sz/mx*100}%"></span><span class="sz">${l.sz.toFixed(2)}</span></div>`).join('');
  }
  render();
  if(!reduced) setInterval(()=>{
    const side=Math.random()<.5?asks:bids, i=Math.floor(Math.random()*3);
    side[i].sz=Math.max(.2,Math.min(3,side[i].sz+(Math.random()-.5)*.7));
    render();
    const rows=$$((side===asks?'#asks':'#bids')+' .lvl');
    if(rows[i]){rows[i].classList.add('flash');setTimeout(()=>rows[i].classList.remove('flash'),500);}
  },1600);
})();

/* ── scrollytelling pipeline ─────────────────── */
(function(){
  const stages=$$('#pipefig .fig-stage');
  const names=['texto','tokens','árbol (AST)','bytecode','la VM ejecuta','1s y 0s'];
  const nameEl=$('#stagename');
  let vmTimer=null;
  const vmStates=[[],['99950'],['99950','100000'],['199950'],['199950','2'],['99975.0'],[]];
  function runVM(){
    clearInterval(vmTimer);
    const rows=$$('#vmByt .row'), stack=$('#vmStack');
    let k=0;
    function tick(){
      rows.forEach((r,i)=>r.classList.toggle('hl',i===k));
      const st=vmStates[Math.min(k+1,vmStates.length-1)];
      stack.innerHTML=st.map(v=>`<div class="cell">${v}</div>`).join('');
      k++;
      if(k>=rows.length){clearInterval(vmTimer);}
    }
    stack.innerHTML='';rows.forEach(r=>r.classList.remove('hl'));
    if(reduced){rows.forEach(r=>r.classList.remove('hl'));rows[rows.length-1].classList.add('hl');
      stack.innerHTML='<div class="cell">99975.0</div>';return;}
    tick();vmTimer=setInterval(tick,950);
  }
  $('#vmReplay').addEventListener('click',runVM);
  function setStage(n){
    stages.forEach(s=>s.classList.toggle('on',+s.dataset.stage===n));
    nameEl.textContent=names[n];
    if(n===4)runVM();else clearInterval(vmTimer);
  }
  const io=new IntersectionObserver(es=>{
    es.forEach(e=>{
      if(e.isIntersecting){
        const st=+e.target.dataset.stage;
        $$('.steps .step').forEach(x=>x.classList.toggle('on',x===e.target));
        setStage(st);
      }
    });
  },{rootMargin:'-42% 0px -42% 0px'});
  $$('.steps .step').forEach(s=>io.observe(s));
})();

/* ── mini tokenizer / parser / compiler ──────── */
const ENV={bid:{v:99950,f:false},ask:{v:100000,f:false},spread:{v:50,f:false},mid:{v:99975,f:true}};
function tokenize(src){
  const toks=[];let i=0;
  while(i<src.length){
    const ch=src[i];
    if(ch===' '||ch==='\t'){i++;continue;}
    if(/[0-9]/.test(ch)){let j=i;while(j<src.length&&/[0-9.]/.test(src[j]))j++;
      const raw=src.slice(i,j);
      if((raw.match(/\./g)||[]).length>1)throw{type:'SyntaxError',msg:`número inválido: ${raw}`};
      toks.push({t:'NUMBER',v:raw});i=j;continue;}
    if(/[A-Za-z_]/.test(ch)){let j=i;while(j<src.length&&/[A-Za-z0-9_]/.test(src[j]))j++;
      toks.push({t:'NAME',v:src.slice(i,j)});i=j;continue;}
    if(ch==='"'||ch==="'"){let j=i+1;while(j<src.length&&src[j]!==ch)j++;
      if(j>=src.length)throw{type:'SyntaxError',msg:'unterminated string literal — falta cerrar la comilla'};
      toks.push({t:'STRING',v:src.slice(i+1,j)});i=j+1;continue;}
    if('+-*/()='.includes(ch)){toks.push({t:'OP',v:ch});i++;continue;}
    throw{type:'SyntaxError',msg:`carácter inesperado: '${ch}'`};
  }
  if(!toks.length)throw{type:'SyntaxError',msg:'no hay nada que analizar'};
  return toks;
}
function parse(toks){
  let pos=0;
  const peek=()=>toks[pos];
  function expr(){let n=term();
    while(peek()&&peek().t==='OP'&&'+-'.includes(peek().v)){const op=toks[pos++].v;n={kind:'BinOp',op,left:n,right:term()};}
    return n;}
  function term(){let n=factor();
    while(peek()&&peek().t==='OP'&&'*/'.includes(peek().v)){const op=toks[pos++].v;n={kind:'BinOp',op,left:n,right:factor()};}
    return n;}
  function factor(){const tk=peek();
    if(!tk)throw{type:'SyntaxError',msg:'la expresión termina antes de tiempo'};
    if(tk.t==='NUMBER'){pos++;return{kind:'Const',v:tk.v};}
    if(tk.t==='STRING'){pos++;return{kind:'Const',v:tk.v,str:true};}
    if(tk.t==='NAME'){pos++;return{kind:'Name',v:tk.v};}
    if(tk.t==='OP'&&tk.v==='('){pos++;const n=expr();
      if(!peek()||peek().v!==')')throw{type:'SyntaxError',msg:"falta cerrar un paréntesis ')'"};
      pos++;return n;}
    throw{type:'SyntaxError',msg:`no esperaba '${tk.v}' aquí`};}
  let root;
  if(toks.length>=2&&toks[0].t==='NAME'&&toks[1].t==='OP'&&toks[1].v==='='){
    pos=2;root={kind:'Assign',target:toks[0].v,value:expr()};}
  else root={kind:'Expr',value:expr()};
  if(pos<toks.length)throw{type:'SyntaxError',msg:`sobra '${toks[pos].v}' al final`};
  return root;
}
function compile(node,out){
  switch(node.kind){
    case 'Const':out.push(['LOAD_CONST',node.str?"'"+node.v+"'":node.v]);break;
    case 'Name':out.push(['LOAD_NAME',node.v]);break;
    case 'BinOp':compile(node.left,out);compile(node.right,out);out.push(['BINARY_OP',node.op]);break;
    case 'Assign':compile(node.value,out);out.push(['STORE_NAME',node.target]);break;
    case 'Expr':compile(node.value,out);break;
  }
}
function evalNode(n){
  if(n.kind==='Const'){
    if(n.str)return{v:n.v,str:true};
    const f=n.v.includes('.');return{v:parseFloat(n.v),f};}
  if(n.kind==='Name'){
    if(!(n.v in ENV))throw{type:'NameError',msg:`name '${n.v}' is not defined`};
    return{...ENV[n.v]};}
  if(n.kind==='BinOp'){
    const a=evalNode(n.left),b=evalNode(n.right);
    const tn=x=>x.str?'str':(x.f?'float':'int');
    if(a.str||b.str){
      if(n.op==='+'&&a.str&&b.str)return{v:a.v+b.v,str:true};
      if(n.op==='*'&&(a.str!==b.str)&&!(a.f||b.f)){
        const s=a.str?a.v:b.v,k=a.str?b.v:a.v;
        return{v:s.repeat(Math.max(0,k)),str:true};}
      if(n.op==='+'&&a.str)throw{type:'TypeError',msg:`can only concatenate str (not "${tn(b)}") to str`};
      throw{type:'TypeError',msg:`unsupported operand type(s) for ${n.op}: '${tn(a)}' and '${tn(b)}'`};}
    let v,f=a.f||b.f;
    if(n.op==='+')v=a.v+b.v;else if(n.op==='-')v=a.v-b.v;
    else if(n.op==='*')v=a.v*b.v;
    else{if(b.v===0)throw{type:'ZeroDivisionError',msg:'division by zero'};v=a.v/b.v;f=true;}
    return{v,f};}
  if(n.kind==='Assign'||n.kind==='Expr')return evalNode(n.value);
}
function fmt(r){if(r.str)return"'"+r.v+"'";return r.f&&Number.isInteger(r.v)?r.v+'.0':String(r.v);}
function treeLines(node){
  const lab=n=>n.kind==='BinOp'?`BinOp ${n.op}`:n.kind==='Const'?`Const ${n.str?"'"+n.v+"'":n.v}`
    :n.kind==='Name'?`Name ${n.v}`:n.kind==='Assign'?`Assign → ${n.target}`:'Expr';
  const kids=n=>n.kind==='BinOp'?[n.left,n.right]:(n.kind==='Assign'||n.kind==='Expr')?[n.value]:[];
  const lines=[lab(node)];
  (function rec(n,pre){
    const ks=kids(n);
    ks.forEach((k,i)=>{const last=i===ks.length-1;
      lines.push(pre+(last?'└─ ':'├─ ')+lab(k));
      rec(k,pre+(last?'   ':'│  '));});
  })(node,'');
  return lines.join('\n');
}
/* own line simulator */
(function(){
  const run=()=>{
    const src=$('#ownIn').value;
    const err=$('#ownErr'),cols=$('#ownCols');
    try{
      const toks=tokenize(src);
      const ast=parse(toks);
      const byt=[];compile(ast,byt);
      const res=evalNode(ast);
      err.classList.add('hidden');cols.classList.remove('hidden');
      $('#ownToks').innerHTML=toks.map(tk=>{
        const cls=tk.t==='NAME'?'name':tk.t==='NUMBER'?'number':tk.t==='STRING'?'stringt':'op';
        const shown=tk.t==='STRING'?'"'+tk.v+'"':tk.v;
        return`<span class="tok ${cls}"><small>${tk.t.toLowerCase()}</small><b>${shown}</b></span>`;}).join('');
      $('#ownAst').textContent=treeLines(ast);
      $('#ownByt').textContent=byt.map((b,i)=>`${i+1}  ${b[0].padEnd(12)}${b[1]}`).join('\n');
      $('#ownEnv').textContent='entorno: bid=99950, ask=100000,\n         spread=50, mid=99975.0';
      $('#ownRes').textContent=(ast.kind==='Assign'?`${ast.target} → `:'resultado → ')+fmt(res)+' ✓';
    }catch(e){
      cols.classList.add('hidden');err.classList.remove('hidden');
      err.textContent=`${e.type||'Error'}: ${e.msg||e.message} — igual que te lo diría Python. Arréglalo y reintenta.`;
    }
  };
  $('#ownRun').addEventListener('click',run);
  $('#ownIn').addEventListener('keydown',e=>{if(e.key==='Enter')run();});
  run();
})();

/* ── §2 predict + run + step-through ─────────── */
(function(){
  const inp=$('#predictIn'),btn=$('#varRun');
  inp.addEventListener('input',()=>btn.disabled=inp.value.trim().length===0);
  btn.addEventListener('click',()=>{
    btn.disabled=true;inp.disabled=true;
    $('#varOut').classList.remove('hidden');
    const target='99975.0',el=$('#varOutVal');
    if(reduced){el.textContent=target;}
    else{let k=0;const t=setInterval(()=>{el.textContent=target.slice(0,++k);
      if(k>=target.length)clearInterval(t);},70);}
    setTimeout(()=>$('#afterRun').classList.remove('hidden'),reduced?0:600);
  });
  /* step-through */
  const steps=[
    {line:0,log:"bid apunta a 99950",row:{n:'bid',v:'99950',t:'int'}},
    {line:1,log:"ask apunta a 100000",row:{n:'ask',v:'100000',t:'int'}},
    {line:2,log:"se evalúa (99950+100000)/2 → mid apunta a 99975.0",row:{n:'mid',v:'99975.0',t:'float'}},
    {line:3,log:"print busca el valor de mid y lo pinta en pantalla",row:null}];
  let i=0;
  const lines=$$('#stepCode .ln'),mem=$('#memory'),log=$('#stepLog');
  function reset(){i=0;lines.forEach(l=>l.classList.remove('hl','dim'));
    mem.innerHTML='<p style="color:var(--faint);font-size:.85rem;margin:0">— memoria vacía —</p>';
    log.textContent='';}
  $('#stepBtn').addEventListener('click',()=>{
    if(i>=steps.length){reset();return;}
    const st=steps[i];
    lines.forEach((l,k)=>{l.classList.toggle('hl',k===st.line);l.classList.toggle('dim',k<st.line);});
    if(i===0)mem.innerHTML='';
    if(st.row)mem.insertAdjacentHTML('beforeend',
      `<div class="mem-row ${st.row.t}"><span class="mem-name">${st.row.n}</span><span class="mem-arrow">─▶</span><span class="mem-val">${st.row.v}<span class="type-chip">${st.row.t}</span></span></div>`);
    log.textContent='» '+st.log;
    i++;
    $('#stepBtn').textContent=i>=steps.length?'↻ otra vez':'Paso ›';
  });
  $('#stepReset').addEventListener('click',()=>{reset();$('#stepBtn').textContent='Paso ›';});
})();

/* ── §3 loop visualizer ──────────────────────── */
(function(){
  const prices=[99950,99975,100010,99990];
  const cellsEl=$('#loopCells');let i=0,total=0,auto=null;
  function render(){
    cellsEl.innerHTML=prices.map((p,k)=>
      `<div class="cell-p ${k===i-1?'cur':k<i-1?'done':''}"><small>prices[${k}]</small>${p}</div>`).join('');
    $('#accIter').textContent=i===0?'—':(i<=prices.length?i+'/4':'4/4');
    $('#accP').textContent=i>=1&&i<=prices.length?prices[i-1]:'—';
    $('#accTotal').textContent=String(total);
    $('#accMedia').textContent=i>prices.length?String(total/prices.length):'—';
  }
  function step(){
    if(i<prices.length){total+=prices[i];i++;
      $('#loopLog').textContent=`» vuelta ${i}: p = ${prices[i-1]} · total = ${total}`;}
    else if(i===prices.length){i++;
      $('#loopLog').textContent=`» fin del bucle · media = total / len(prices) = ${(total/prices.length)}`;
      stopAuto();}
    render();
  }
  function reset(){i=0;total=0;$('#loopLog').textContent='pulsa Paso para entrar en el bucle';stopAuto();render();}
  function stopAuto(){clearInterval(auto);auto=null;$('#loopAuto').textContent='▶▶ Auto';}
  $('#loopStep').addEventListener('click',()=>{if(i>prices.length)reset();else step();});
  $('#loopAuto').addEventListener('click',()=>{
    if(auto){stopAuto();return;}
    if(i>prices.length)reset();
    $('#loopAuto').textContent='∥ Parar';
    auto=setInterval(()=>{step();if(i>prices.length)stopAuto();},reduced?600:850);
  });
  $('#loopReset').addEventListener('click',reset);
  render();
})();

/* ── §4 dict hover link + venue ──────────────── */
(function(){
  function link(key,on){
    $$(`[data-key="${key}"]`).forEach(el=>el.classList.toggle('hl',on));
  }
  $$('.dk,.oc-row').forEach(el=>{
    el.addEventListener('mouseenter',()=>link(el.dataset.key,true));
    el.addEventListener('mouseleave',()=>link(el.dataset.key,false));
  });
  $('#venueBtn').addEventListener('click',()=>{
    if($('.oc-row[data-key=venue]'))return;
    $('.ordercard').insertAdjacentHTML('beforeend',
      '<div class="oc-row new" data-key="venue"><span class="kk">venue</span><span class="vv">binance</span></div>');
    $('#venueMsg').textContent='✓ campo añadido a la ficha';
    $('#venueMsg').style.color='var(--bid)';
  });
})();

/* ── §5 slider decision ──────────────────────── */
(function(){
  const sl=$('#spSlider');
  function update(){
    const v=+sl.value;$('#spVal').textContent=v;
    const br=v<20?0:v<80?1:2;
    const txt=['"líquido: cruzar ya"','"aceptable: limit al mid"','"ilíquido: esperar"'][br];
    $$('#ifCode .ln').forEach(l=>{
      const b=+l.dataset.br;l.classList.toggle('hl',b===br);l.classList.toggle('dim',b!==br);});
    $('#verdictTxt').textContent=txt;
  }
  sl.addEventListener('input',update);update();
})();

/* ── §7 final run + quiz ─────────────────────── */
(function(){
  $('#finalRun').addEventListener('click',()=>{
    const out=$('#finalOut');out.classList.remove('hidden');
    const rows=[...out.children];
    rows.forEach((r,k)=>{r.style.opacity=0;
      setTimeout(()=>{r.style.transition='opacity .4s';r.style.opacity=1;},reduced?0:300*(k+1));});
    $('#finalRun').disabled=true;$('#finalRun').textContent='✓ ejecutado';
  });
  let answered=0,right=0;
  const total=$$('.q').length;
  $$('.q').forEach(q=>{
    const ok=+q.dataset.ok;
    const opts=[...q.querySelectorAll('.opt')];
    opts.forEach((o,idx)=>o.addEventListener('click',()=>{
      opts.forEach(x=>x.disabled=true);
      opts[ok].classList.add('ok');
      if(idx!==ok)o.classList.add('bad');else right++;
      q.querySelector('.why').classList.add('show');
      answered++;
      if(answered===total)$('#score').textContent=
        `Resultado: ${right}/${total}`+(right===total?' — impecable.':right>=3?' — sólido; revisa las que fallaste.':' — relee las secciones marcadas y reintenta mañana.');
    }));
  });
})();
})();
