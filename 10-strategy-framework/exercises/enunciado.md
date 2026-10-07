# L10 · Una máquina. Muchas estrategias.

**Objetivo.** Probar distintas estrategias con el mismo reloj, matching y contabilidad.
Construyes Hold/BuyOnce/SellOnce y conectas ResearchBacktest; las bases y contratos ya están aquí.

Edita `strategy.py`, `runner.py` y `main.py`. Empieza en **1A**,
`Hold.on_book_update`, con `python main.py --through 1A` desde `exercises`.
La plantilla imprime el escenario y «Completa 1A en strategy.py»; es su estado esperado.
Después usa `--through 1B`, `--through 1C`… para parar antes de los apartados futuros.
Conserva tu intento personal antes de consultar la solución. Al reiniciar el proceso
se cargan tus clases editadas; no traslades archivos de otra lesson.

| Archivo | Papel |
|---|---|
| `strategy.py` | A completar: reglas y reset de BuyOnce; on_fill/on_end están proporcionados. |
| `runner.py` | A completar: comisión, contadores y conexiones del runner; el bucle/guardias/registros están proporcionados. |
| `main.py` | A completar: peticiones y experimentos 2A–4E; contiene las comprobaciones del recorrido. |
| `market.py`, `matching.py`, `book.py`, `adapters.py`, `base_book.py`, `portfolio.py` | Bases locales completas incorporadas desde sus respuestas canónicas. No modificarlas. |
| `scenarios.py` | Dos fotos y helpers de referencia proporcionados. |
| `exchange/` | Order/OrderType/ExecutionFill, Strategy/NewOrder y Context proporcionados; el Backtest tipado es referencia, no sustituye ResearchBacktest. |
| `opcionales.py` | Variantes 5A–5C OPTIONAL; no sostienen la ruta requerida. |
| `solutions/solucion.md` | Respuestas por apartado y archivos resueltos completos. |

**Contratos.** `Strategy` es una ABC: toda hija implementa `on_book_update(book)` y
retorna una lista. `[]` no pide actuar; `[NewOrder(order)]` pide enviar una orden.
El runner ejecuta y llama `on_fill(fill)` por cada ejecución; la hija no registra otra
vez el fill en la cartera. `on_start(ctx)`/`on_end(ctx)` se llaman al principio/al final.
`Context(market,tracker)` consulta timestamp, mid y position, sin copiar la contabilidad.
`ReplayMarket.step()` entrega libro/None; `submit(order)` devuelve fills sin avanzar.
`PositionTracker.apply_fill(fill)` cambia caja/posición; `equity(mark)` solo valora.
Un fill tiene side,price,size,timestamp y cash_flow(). Son interfaces incluidas, no nuevos ejercicios.

**Datos y límites.** Dos fotos sintéticas, mid 100→102, precios USDT/BTC, tamaños BTC,
timestamp 0/1 como orden docente. Caja 1000 y posición 0 al empezar cada run. Foto 0:
bid 99×2, asks 101×0.4/102×0.6; foto 1: bid 101×2, ask 103×1. Procedencia y CSV de referencia
en `exchange/_data/README.md`. Captura el mid antes de ejecutar: puede desaparecer si
se agota un lado. ResearchBacktest acepta únicamente NewOrder MARKET/IOC; rechaza
Cancel/LIMIT/FOK. Excluir FOK es una decisión de alcance, no una afirmación de que sea
pasivo. Sin cola de órdenes entre fotos, restricción de financiación ni margen; la
variante SellOnce permite posición negativa. 1bps=1/10000; se cobra sobre cada fill.

**Autonomía.** El contrato y los hooks nuevos se guían. En 2C combina el registro y
la notificación; en 4A–4E decide qué observar para justificar repetición, costes y
liquidez. Escribe la predicción de 4E antes de ejecutar; OPTIONAL no es necesario.


## Ejercicio 1 · Reglas con un contrato común

### 1A · Hold.on_book_update

**Dónde:** `strategy.py` → `Hold.on_book_update`.

**Qué y para qué:** Devuelve [] desde Hold.on_book_update: observar el libro no obliga a enviar una orden.

**Comprueba:** `python main.py --through 1A`.

<details><summary>Resultado para contrastar después del intento</summary>

Hold propone [] y no genera ningún fill. Strategy es el contrato proporcionado; implementas su hija.

</details>

### 1B · BuyOnce.on_start

**Dónde:** `strategy.py` → `BuyOnce.on_start`.

**Qué y para qué:** Reinicia done, callbacks, executed y end_position en BuyOnce.on_start para repetir la misma estrategia.

Usa los cuatro atributos ya inicializados. La política de compra no cambia; reiniciar permite usar la misma instancia.

**Comprueba:** `python main.py --through 1B`.

<details><summary>Resultado para contrastar después del intento</summary>

on_start restablece False, 0, 0.0 y None. La misma instancia puede empezar de nuevo.

</details>

### 1C · BuyOnce.on_book_update

**Dónde:** `strategy.py` → `BuyOnce.on_book_update`.

**Qué y para qué:** Propón una única NewOrder MARKET de self.size usando book.symbol; después devuelve [].

done distingue primera/segunda consulta. Una propuesta no aumenta executed; ese acumulador lo modifica el on_fill proporcionado.

**Comprueba:** `python main.py --through 1C`.

<details><summary>Resultado para contrastar después del intento</summary>

Primera consulta: una NewOrder. Segunda: []. done cuenta la propuesta; executed sigue en 0.

</details>


## Ejercicio 2 · De intención a confirmación

### 2A · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Guarda la primera petición en action e inspecciona la orden sin enviarla ni cambiar la cartera.

first_actions está proporcionada por 1C. No llames submit aquí: contrasta caja/posición antes del envío.

**Comprueba:** `python main.py --through 2A`.

<details><summary>Resultado para contrastar después del intento</summary>

action.order es BUY 1; crear o inspeccionar esa petición deja caja 1000 y posición 0.

</details>

### 2B · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Avanza manual_market, captura su mid antes de ejecutar y envía action.order; guarda active_book, mark y confirmed.

Usa una sola foto y captura mark antes de submit: el matching puede agotar el ask y dejar mid=None.

**Comprueba:** `python main.py --through 2B`.

<details><summary>Resultado para contrastar después del intento</summary>

Se confirman 101×0.4 y 102×0.6. mark era 100; el ask queda vacío y mid posterior es None. La cartera aún no registra nada.

</details>

### 2C · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Aplica cada fill confirmado a tracker, llama strategy.on_fill por cada uno y guarda first_equity al mark previo.

Usa confirmed y mark de 2B. Predice caja, posición, número de callbacks y cantidad. Después el código proporcionado avanza a otra foto y muestra la nueva valoración.

**Comprueba:** `python main.py --through 2C`.

<details><summary>Resultado para contrastar después del intento</summary>

Caja 898.4, posición 1, equity 998.4 al mark 100. Dos callbacks suman 1 BTC. En la segunda foto no hay orden y equity 1000.4 al mid 102.

</details>


## Ejercicio 3 · Un runner que conecta las piezas

### 3A · FeePortfolio.charge

**Dónde:** `runner.py` → `FeePortfolio.charge`.

**Qué y para qué:** Resta fee de self.cash en FeePortfolio.charge; conserva la validación proporcionada.

**Comprueba:** `python main.py --through 3A`.

<details><summary>Resultado para contrastar después del intento</summary>

charge(.1016) deja 999.8984 en la sonda aislada. La compra cobra solo sobre su importe confirmado, no por foto.

</details>

### 3B · ResearchResult.n_steps y n_fills

**Dónde:** `runner.py` → `ResearchResult.n_steps y n_fills`.

**Qué y para qué:** Deriva n_steps de equity_curve y n_fills de fills, sin contadores independientes.

Conserva las listas y los atributos finales proporcionados. Las dos properties llevan este mismo apartado.

**Comprueba:** `python main.py --through 3B`.

<details><summary>Resultado para contrastar después del intento</summary>

El contenedor vacío devuelve 0 pasos y 0 fills. Una foto puede tener cero o muchos fills; n_steps no es n_fills.

</details>

### 3C · ResearchBacktest.run

**Dónde:** `runner.py` → `ResearchBacktest.run`.

**Qué y para qué:** Llama on_start(ctx) antes del bucle de ResearchBacktest.run para reiniciar la estrategia.

La sonda StartProbe proporcionada solo comprueba la llamada de inicio; no es otra tarea. Con Hold no se ejecuta el bloque 3D. Los hooks pendientes del runner usan pass para poder probar por etapas; sustituye cada pass por su llamada.

**Comprueba:** `python main.py --through 3C`.

<details><summary>Resultado para contrastar después del intento</summary>

reset limpia el mercado; se crean cartera y resultado nuevos. on_start reinicia la estrategia. StartProbe, proporcionada, devuelve started=True; Hold da [1000,1000].

</details>

### 3D · ResearchBacktest.run

**Dónde:** `runner.py` → `ResearchBacktest.run`.

**Qué y para qué:** Registra cada fill en la cartera, cobra su fee una vez y notifica strategy.on_fill(fill).

Actúa en los tres comentarios 3D: aplicar el fill, cobrar fee y notificar. El nominal, cálculo de fee y registros ya están escritos. No cobres por foto ni por la cantidad solicitada.

**Comprueba:** `python main.py --through 3D`.

<details><summary>Resultado para contrastar después del intento</summary>

Cada ejecución alimenta cartera, fee y callback. BuyOnce(1) genera 2 fills y curva [998.4,1000.4]. Registrar el envío no equivale a contabilizarlo.

</details>

### 3E · ResearchBacktest.run

**Dónde:** `runner.py` → `ResearchBacktest.run`.

**Qué y para qué:** Llama on_end(ctx) tras la contabilidad final y antes de devolver el resultado.

La cuenta ya está cerrada. Comprueba BuyOnce.end_position, no vuelvas a aplicar fills.

**Comprueba:** `python main.py --through 3E`.

<details><summary>Resultado para contrastar después del intento</summary>

on_end observa posición 1, después de las operaciones y antes del return. Se devuelve un resultado independiente.

</details>


## Ejercicio 4 · Cambiar y justificar el experimento

### 4A · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Ejecuta otra vez el mismo runner y guarda repeated, sin crear otra estrategia.

Usa el runner de 3E. No crees una estrategia nueva para ocultar un fallo de on_start.

**Comprueba:** `python main.py --through 4A`.

<details><summary>Resultado para contrastar después del intento</summary>

La repetición del mismo runner mantiene curva [998.4,1000.4], posición 1 y callbacks 2. No acumula posición 2 ni cuatro callbacks.

</details>

### 4B · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Compara callbacks con n_fills y executed con la suma de tamaños de repeated; guarda ambas comprobaciones.

Usa repeated y runner.strategy; la comparación de cantidad no utiliza el número de órdenes enviadas.

**Comprueba:** `python main.py --through 4B`.

<details><summary>Resultado para contrastar después del intento</summary>

True/True: callbacks==2 y executed==0.4+0.6. Contar confirmaciones y sumar cantidades son medidas distintas.

</details>

### 4C · SellOnce.on_book_update

**Dónde:** `strategy.py` → `SellOnce.on_book_update`.

**Qué y para qué:** Sobrescribe solo SellOnce.on_book_update para proponer una venta MARKET única del tamaño configurado.

Hereda on_start/on_fill/on_end de BuyOnce. Solo cambia el lado; el runner permanece igual.

**Comprueba:** `python main.py --through 4C`.

<details><summary>Resultado para contrastar después del intento</summary>

SellOnce(0.5) usa el mismo runner: caja 1049.5, posición-0.5 y equity 998.5. El ejemplo permite posición corta y no modela margen.

</details>

### 4D · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Ejecuta Hold y BuyOnce(1) con 10 bps sobre las mismas filas; guarda hold_result y cost_result.

fee_bps=10 significa 0.1%. El result de 3E usó 0 bps: explica qué cambia y qué permanece igual al compararlo con cost_result.

**Comprueba:** `python main.py --through 4D`.

<details><summary>Resultado para contrastar después del intento</summary>

Hold: [1000,1000], fees 0. BuyOnce(1): [998.2984,1000.2984], fees 0.1016. Misma ejecución y posición, caja menor por ese coste.

</details>

### 4E · practice

**Dónde:** `main.py` → `practice`.

**Qué y para qué:** Predice BuyOnce(3), ejecuta liquidity_runner y repite la misma instancia; guarda liquidity_result y liquidity_repeat.

**Transferencia REQUIRED: predice antes de ejecutar.** Sin cambiar rows ni las clases, pide 3 BTC con BuyOnce(3), fee_bps=0 y cash 1000. ¿Qué significan size, done, executed y posición? ¿La segunda foto completa lo que falta? Repite el mismo runner y explica si acumula la compra anterior. Esta variación distingue propuesta, confirmación y reinicio; no es otra entrega.

**Comprueba:** `python main.py --through 4E`.

<details><summary>Resultado para contrastar después del intento</summary>

Se solicitan 3 BTC; done=True, executed=1 y posición 1. Solo hay 1 BTC de ask en la foto 0. No se reenvían los 2 pendientes: BuyOnce significa una propuesta. Repetir limpia todo: los mismos 2 fills, posición 1 y callbacks 2. La prueba distingue intención de ejecución, no acredita que la regla complete objetivos.

</details>


## Ejercicio 5 · Variantes OPTIONAL

### 5A · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: copia rows en partial_rows, elimina el segundo ask de la primera foto y ejecuta BuyOnce(1).

OPTIONAL. No modifiques rows original. ¿La segunda foto completa el tamaño pendiente?

**Comprueba:** `python opcionales.py --through 5A`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. Al quitar el segundo ask se ejecutan 0.4 BTC y un fill; curva [999.6,1000.4]. La segunda foto no completa lo pendiente.

</details>

### 5B · practice · OPTIONAL

**Dónde:** `opcionales.py` → `practice`.

**Qué y para qué:** OPTIONAL: ejecuta dos veces el mismo replay_runner y compara sus curvas y posiciones en same_result.

OPTIONAL. Conserva la misma instancia de estrategia entre las dos llamadas a run.

**Comprueba:** `python opcionales.py --through 5B`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. True: curvas y posiciones iguales en ambas ejecuciones de la misma instancia; resultados distintos como objetos.

</details>

### 5C · ImbalanceBuyer.on_book_update · OPTIONAL

**Dónde:** `opcionales.py` → `ImbalanceBuyer.on_book_update`.

**Qué y para qué:** OPTIONAL: compra 0.1 MARKET si imbalance(1)>0.3; en None, igualdad o valores inferiores devuelve [].

OPTIONAL. Consulta imbalance una sola vez. La igualdad y None no compran. Usa book.symbol; esta regla puede pedir una orden en cada foto admisible.

**Comprueba:** `python opcionales.py --through 5C`.

<details><summary>Resultado para contrastar después del intento</summary>

OPTIONAL. En estas fotos la regla compra 0.1 cada vez: 2 fills, posición 0.2. None y el umbral exacto no compran. El resultado del fixture no demuestra predicción.

</details>

## Cierre

Ejecuta `python main.py`: has conectado intención, ejecución, cartera y feedback; puedes cambiar estrategia y repetir con el mismo runner. L11 conservará estos resultados para comparar coste, riesgo y exposición. OPTIONAL: `python opcionales.py`, solo si eliges esas variantes.
