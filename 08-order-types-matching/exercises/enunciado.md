# Lesson 8 · Tu orden pide. El mercado pone las condiciones.

Vas a construir un matching engine que recibe una orden y un libro, decide qué
puede ejecutarse y, solo después de validar, consume liquidez y devuelve fills.
Tu implementación se llama `PlannedEngine`. `process(order, book, timestamp=None)`
es la llamada que conectará tu motor con el backtest.

## Inicio y archivos

Todo está en esta carpeta. Abre `matching.py` y `main.py`; guarda una copia personal
de la carpeta para conservar tus intentos. Desde `exercises`, ejecuta `python main.py`.
La plantilla ya muestra el libro inicial y señala 1A. Los apartados posteriores
pueden seguir pendientes: `python main.py --through 1A` detiene la observación ahí.
Un aviso `Completa …` es el estado incompleto esperado; no necesitas abrir otra lesson.

| Archivo | Papel |
| --- | --- |
| matching.py | EDITABLE: funciones y PlannedEngine. Todos los TODO de este archivo son nuevos. |
| main.py | EDITABLE: intenciones, experimentos y cuentas. No define las clases de mercado. |
| base_book.py, adapters.py, book.py | Bases completas de L5/L7, ya incluidas. Sus comentarios son procedencia, no tareas actuales. |
| scenarios.py | Proporcionado: fresh_book crea niveles nuevos; firmas legibles para comparar estados. |
| exchange/orders.py, exchange/trades.py | API proporcionada: Order, Side, OrderType y ExecutionFill. No hay que implementarlos. |
| exchange/book.py, exchange/matching.py | Referencia independiente usada únicamente en el contraste 6B. No sustituye tu PlannedEngine. |
| exchange/_data/ | CSV sintético y explicación de procedencia/formato. |
| opcionales.py | Variantes 7A–7D después del principal; no necesarias para continuar. |
| solutions/solucion.md | Respuesta completa y comentada por archivo. |

## Contratos y bancos de pruebas

`Order('BTC','buy',1,order_type=OrderType.MARKET)` expresa una intención.
`Side` normaliza buy/sell. MARKET usa price=None; en este modelo LIMIT, IOC y FOK
requieren price. MARKET/LIMIT distinguen precio; IOC/FOK añaden condiciones de
ejecución. Para simplificar el ejercicio, OrderType reúne estas cuatro combinaciones.

`ExecutionFill(order_id,symbol,side,price,size,timestamp)` representa una ejecución;
`cash_flow()` devuelve caja negativa al comprar y positiva al vender.
El motor modifica el mismo libro; ni avanza tiempo ni actualiza una cartera.

Control pequeño: bid 99×1 y asks 101×0.4, 102×1.6. Precio USD/BTC, tamaño BTC.
`fresh_book()` devuelve otra instancia para comparar políticas desde igual liquidez.
En 6A cambiamos al primer snapshot del CSV sintético: texto, USDT/BTC y BTC.
La factory incluida conoce ambos formatos de fila. No son datos reales del día de L7.
LIMIT descansa solo en la foto actual: no modelamos órdenes individuales ni prioridad
de cola; al avanzar, L9 reconstruye la foto. EPS=1e-12 evita residuos muy pequeños.

## Ejercicio 1 · Elegir liquidez y precio — LIVE

### 1A · Selecciona el lado contrario

**Dónde:** `matching.py` / `opposite_levels`.

**Encargo:** Devuelve los asks para BUY y los bids para SELL, conservando la lista del libro.

Completa opposite_levels devolviendo la lista de asks para BUY y de bids para SELL. Usamos Order/Side/OrderType del paquete: Side convierte buy/sell en enum compatible con esos textos; MARKET no tiene límite, las otras políticas requieren price.

**Comprobación:** `python main.py --through 1A`.

<details><summary>Contrastar después del intento</summary>

`[(101.0,0.4),(102.0,1.6)]` y `True`. El primer ejemplo es exactamente el de la presentación.

Seleccionar no copia ni modifica liquidez; el plan seguirá apuntando a esos niveles.

</details>

<details><summary>Ayuda</summary>

Una compra consume ofertas de venta; conserva las referencias a sus objetos.

</details>

### 1B · Calcula take y remaining

**Dónde:** `matching.py` / `take_from_level`.

**Encargo:** Devuelve take = min(remaining, level.size) y el nuevo pendiente, sin modificar el nivel.

Completa take_from_level: toma como máximo lo pendiente y el tamaño del nivel; devuelve (take, nuevo_remaining). Predice ambas cifras al pedir una unidad al primer ask.

**Comprobación:** `python main.py --through 1B`.

<details><summary>Contrastar después del intento</summary>

`0.4 0.6`; el nivel conserva `0.4`.

La misma operación se reutiliza en cada tramo del plan.

</details>

<details><summary>Ayuda</summary>

min elige la cantidad admisible. Restar aquí actualiza el pendiente, no level.size.

</details>

### 1C · Decide si el precio cruza

**Dónde:** `matching.py` / `crosses`.

**Encargo:** Acepta cualquier precio en MARKET; en las demás políticas compara el límite según BUY o SELL.

Completa crosses. MARKET admite todo precio; BUY con límite admite precios menores o iguales y SELL mayores o iguales. Predice qué hará una compra con límite 101 ante los dos asks.

**Comprobación:** `python main.py --through 1C`.

<details><summary>Contrastar después del intento</summary>

`[True, False]`. El límite restringe precio, no exige por sí solo ejecución completa.

La igualdad cruza; la misma condición sirve a LIMIT, IOC y FOK con precio.

</details>

<details><summary>Ayuda</summary>

Comprueba MARKET antes de comparar con price, que allí es None.

</details>

## Ejercicio 2 · Planificar y confirmar — LIVE

### 2A · Construye un único plan

**Dónde:** `matching.py` / `plan_fills`.

**Encargo:** Construye pares (level, take) con crosses y take_from_level; devuelve plan y pendiente sin mutar.

Completa plan_fills usando crosses y take_from_level. Devuelve pares (level,take) y el remanente; detente al completar la cantidad o al primer precio no admisible. Cada level es una referencia al objeto, no su precio aislado.

**Comprobación:** `python main.py --through 2A`.

<details><summary>Contrastar después del intento</summary>

`[(101.0,0.4),(102.0,0.6)]`, `0.0`; tamaños intactos `[0.4,1.6]`.

El formato del plan permanece igual en MARKET, LIMIT, IOC y FOK.

</details>

<details><summary>Ayuda</summary>

Conserva el objeto en plan.append((level,take)); su precio se leerá al crear el fill.

</details>

### 2B · Aplica el plan y crea fills

**Dónde:** `matching.py` / `commit_plan`.

**Encargo:** Consume cada par del plan, crea ExecutionFill con timestamp y retira niveles agotados.

Completa commit_plan: resta cada take al Level y crea un ExecutionFill con los metadatos de la orden. Después filtra niveles agotados conservando las listas del libro; este paso aplica un plan ya autorizado, todavía MARKET.

**Para depurar y repetir.** El plan conserva referencias a los niveles de ese libro: después de commit su liquidez ha cambiado y no debes aplicar de nuevo el mismo plan. La observación reconstruye libro y orden, selecciona niveles y recalcula el plan con tus funciones antes de cada commit. Puedes repetirla para comparar el mismo experimento, sin inventar una segunda ejecución sobre liquidez consumida. Esto no convierte `commit_plan` en idempotente ni es una comprobación automática de comprensión.

**Comprobación:** `python main.py --through 2B`.

<details><summary>Contrastar después del intento</summary>

Fills `(101,0.4)` y `(102,0.6)`; queda ask `(102,1.0)`. Timestamp `7`, caja `-101.6`.

Aquí empieza la mutación. En FOK deberá haber una validación anterior a esta llamada.

</details>

<details><summary>Ayuda</summary>

ExecutionFill(order.id, order.symbol, order.side, level.price, take, timestamp). La asignación lista[:] conserva el objeto lista.

</details>

## Ejercicio 3 · Condiciones de ejecución — REQUIRED

### 3A · Recupera una foto limpia

**Dónde:** `main.py` / `practice`.

**Encargo:** Crea clean con fresh_book y consulta su mid y spread antes de comparar políticas.

Crea clean con fresh_book y guarda mid0 y spread0. Explica por qué la foto anterior ya no sirve como punto de partida idéntico después del commit.

**Comprobación:** `python main.py --through 3A`.

<details><summary>Contrastar después del intento</summary>

`100.0 2.0`.

Comparar órdenes requiere empezar desde el mismo estado inicial.

</details>

<details><summary>Ayuda</summary>

fresh_book reconstruye desde la fila; no reutiliza los Level consumidos.

</details>

### 3B · Recupera la liquidez

**Dónde:** `main.py` / `practice`.

**Encargo:** Guarda available como la profundidad ask de clean en dos niveles.

Consulta available con clean.depth para dos niveles sell. Predice si una compra de 3 puede completarse usando solo esta foto.

**Comprobación:** `python main.py --through 3B`.

<details><summary>Contrastar después del intento</summary>

`2.0` unidades, insuficientes para 3.

La cantidad pedida y la liquidez disponible no son lo mismo.

</details>

<details><summary>Ayuda</summary>

Una compra consume el lado sell.

</details>

### 3C · Un límite detiene el plan

**Dónde:** `main.py` / `practice`.

**Encargo:** Planifica BUY 1 a 101 y SELL 1.5 a 99 sobre clean; conserva sus planes y pendientes.

Guarda una compra LIMIT de 1 a 101 en `limit_order`. Sobre `clean`, usa `opposite_levels` y `plan_fills` para obtener `limit_plan` y `limit_remaining`. Guarda una venta LIMIT de 1.5 a 99 en `sell_order` y obtén `sell_plan` y `sell_remaining` sobre el mismo `clean`. Ambos planes deben dejar sus niveles intactos.

**Comprobación:** `python main.py --through 3C`.

<details><summary>Contrastar después del intento</summary>

Compra: `[(101.0,0.4)]`, pendiente `0.6`; venta: `[(99.0,1.0)]`, pendiente `0.5`.

La condición es simétrica, y planificar sigue sin consumir.

</details>

<details><summary>Ayuda</summary>

El primer precio que no cruza termina el recorrido; los lados ya están ordenados.

</details>

### 3D · Un remanente LIMIT descansa

**Dónde:** `matching.py` / `rest_limit`.

**Encargo:** Añade el remanente LIMIT al lado propio, agrega cantidades al mismo precio y conserva el orden.

Completa rest_limit para añadir el remanente al lado de la orden. Si ya existe ese precio, suma su tamaño; si no, crea un Level y vuelve a ordenar el lado. No registres un fill por la cantidad que descansa.

**Comprobación:** `python main.py --through 3D`.

<details><summary>Contrastar después del intento</summary>

Fill `101×0.4`; bids `[(101,0.6),(99,1)]`. El remanente no es una ejecución.

Agregar liquidez al mismo precio conserva un nivel por precio. Esto modela el libro actual, no garantiza ejecución futura.

</details>

<details><summary>Ayuda</summary>

for/else ejecuta el else solo si no hubo break; puedes expresar esa búsqueda con otra estructura equivalente.

</details>

### 3E · IOC cancela el resto

**Dónde:** `main.py` / `practice`.

**Encargo:** Ejecuta el plan IOC BUY 1 a 101 sobre un libro nuevo y cancela el pendiente.

Crea `ioc_book = fresh_book()` e `ioc_order`: IOC BUY de 1 a 101. Selecciona sus niveles y guarda `ioc_plan` e `ioc_remaining` con `plan_fills`. Aplica solo ese plan y guarda `ioc_fills`; no llames a `rest_limit`. La observación consulta los fills, el pendiente y los bids de `ioc_book`.

**Comprobación:** `python main.py --through 3E`.

<details><summary>Contrastar después del intento</summary>

`0.4 / 0.6`; los bids siguen `[(99,1)]`.

Enviar una IOC no confirma la ejecución de su cantidad total.

</details>

<details><summary>Ayuda</summary>

El cruce coincide con LIMIT; la diferencia es qué haces con remaining.

</details>

### 3F · Valida FOK antes de mutar

**Dónde:** `matching.py` / `validate_plan`.

**Encargo:** Acepta FOK solo si el pendiente es cero dentro de EPS; las demás políticas admiten parciales.

Completa validate_plan(order,remaining): FOK solo permite commit si no queda cantidad; las otras políticas aceptan ejecución parcial. En la comprobación proporcionada, autoriza o aborta antes de llamar a commit_plan y contrasta todos los niveles.

**Comprobación:** `python main.py --through 3F`.

<details><summary>Contrastar después del intento</summary>

`0` fills; asks `[(101,0.4),(102,1.6)]`. Con 3 pedidos y 2 admisibles, no se cambia ningún nivel.

La decisión depende del remanente de tu plan, que todavía no ha cambiado el libro.

</details>

<details><summary>Ayuda</summary>

Una validación posterior al commit llega tarde: devolver [] no restaura tamaños.

</details>

## Ejercicio 4 · Un motor que compone las fases — REQUIRED

### 4A · Integra tus fases en PlannedEngine

**Dónde:** `matching.py` / `PlannedEngine`.

**Encargo:** Conecta selección, plan, validación, commit y remanente LIMIT en process; transmite timestamp.

Completa `process` en una sola clase: selección → plan → validación → commit → remanente LIMIT. Reutiliza tus funciones y transmite `timestamp`. Si orden y libro tienen distinto `symbol`, lanza `ValueError` antes de mutar. Devuelve la lista de fills; una FOK rechazada devuelve `[]`. Cada ejecución de la comprobación carga tu módulo y crea un motor nuevo.

**Comprobación:** `python main.py --through 4A`.

<details><summary>Contrastar después del intento</summary>

MARKET ejecuta 0.4+0.6; LIMIT e IOC ejecutan 0.4, pero solo LIMIT añade bid 101×0.6; FOK no ejecuta ni cambia el libro.

Un único process integra tus respuestas; ninguna importación sustituye el matching aprendido.

</details>

<details><summary>Ayuda</summary>

No repitas los bucles internos de las funciones. Devuelve [] inmediatamente si validate_plan falla.

</details>

### 4B · Una orden pequeña cabe

**Dónde:** `main.py` / `practice`.

**Encargo:** Ejecuta MARKET BUY 0.2 sobre un libro nuevo con tu PlannedEngine y guarda small_fills.

Usa tu engine con una compra MARKET de 0.2 sobre fresh_book y guarda small_fills. Predice cuántos fills habrá y el precio efectivo.

**Comprobación:** `python main.py --through 4B`.

<details><summary>Contrastar después del intento</summary>

Un fill a `101.0` por `0.2`.

Dos tamaños distintos que caben en el mismo nivel pueden tener el mismo precio efectivo.

</details>

<details><summary>Ayuda</summary>

El primer ask tiene 0.4 disponibles.

</details>

## Ejercicio 5 · Leer el resultado económico — REQUIRED

### 5A · Calcula precio efectivo

**Dónde:** `matching.py` / `effective_price`.

**Encargo:** Devuelve el precio ponderado por tamaño de los fills, o None cuando no hay ejecución.

Define effective_price(fills) como suma precio×cantidad dividida por cantidad total; devuelve None si no hubo fills. Aplícala a una MARKET de una unidad sobre una foto nueva.

**Comprobación:** `python main.py --through 5A`.

<details><summary>Contrastar después del intento</summary>

`101.6` USD/unidad; no es la media simple de 101 y 102.

La función observa fills confirmados, no la cantidad solicitada.

</details>

<details><summary>Ayuda</summary>

Pondera cada precio por el tamaño realmente ejecutado.

</details>

### 5B · Coste respecto al mid

**Dónde:** `main.py` / `practice`.

**Encargo:** Guarda buy_slippage = eff - mid inicial y explica el coste positivo de esta compra.

Guarda buy_slippage como eff menos el mid de la foto inicial limpia. Explica por qué una compra tiene coste positivo al pagar por encima del mid.

**Comprobación:** `python main.py --through 5B`.

<details><summary>Contrastar después del intento</summary>

Aproximadamente `1.6` USD/unidad.

Para una venta, el coste simétrico sería mid menos precio efectivo.

</details>

<details><summary>Ayuda</summary>

El mid inicial es una referencia de precio; no es necesariamente ejecutable.

</details>

### 5C · Mide el barrido

**Dónde:** `main.py` / `practice`.

**Encargo:** Suma los tamaños de sweep_fills en executed y cuenta sus fills en levels_used.

Guarda executed y levels_used desde sweep_fills. Contrasta la cantidad pedida con la ejecutada: recorrer dos niveles no crea dos órdenes.

**Comprobación:** `python main.py --through 5C`.

<details><summary>Contrastar después del intento</summary>

`1.0 2`.

Una intención puede confirmarse en varios fills a distintos precios.

</details>

<details><summary>Ayuda</summary>

Cuenta los fills y suma sus tamaños.

</details>

## Ejercicio 6 · Cambiar el dato y contrastar — REQUIRED

### 6A · Tu motor llega al CSV

**Dónde:** `main.py` / `practice`.

**Encargo:** Construye csv_book, pide FOK por el doble de su liquidez ask y conserva csv_fills.

La fila `csv_row` ya está leída. Construye `csv_book` con símbolo BTCUSDT y diez niveles, guarda `csv_available = csv_book.depth('sell',10)` y crea `csv_order`: FOK BUY por el doble de `csv_available`, al precio del último ask. Ejecuta con tu `engine` y guarda `csv_fills`. La MARKET de 0.1 sobre otra copia ya está proporcionada debajo: no tienes que escribirla.

**Comprobación:** `python main.py --through 6A`.

<details><summary>Contrastar después del intento</summary>

FOK devuelve 0 fills y conserva toda la liquidez; la MARKET de 0.1 ejecuta a `100021.8`.

La ruta final conserva tanto tu conversión de L7 como todas las fases de L8.

</details>

<details><summary>Ayuda</summary>

FOK valida el remanente antes del primer commit; ninguna prueba necesita MatchingEngine de referencia.

</details>

### 6B · Contrasta con un oráculo explícito

**Dónde:** `matching.py` / `compare_engine`.

**Encargo:** Compara los fills y ambos lados finales de tu motor con la referencia sobre libros nuevos.

Completa `compare_engine` y devuelve un bool. Crea un libro con `fresh_book()` y otro con `ReferenceBook('BTC', [ReferenceLevel(99,1)], [ReferenceLevel(101,.4), ReferenceLevel(102,1.6)])`. Ejecuta órdenes equivalentes con los argumentos recibidos: tu primer motor debe ser `engine_class()` y el segundo `ReferenceEngine()`. Compara `fill_signature` de ambos resultados y `book_state` de ambos libros; los dos deben coincidir. La observación ya prueba las cuatro políticas y ambos lados.



**Comprobación:** `python main.py --through 6B`.

<details><summary>Contrastar después del intento</summary>

Ocho `True`: coinciden fills y niveles finales. Los ids de órdenes distintas se omiten al comparar.

La igualdad se verifica sobre fills y libros completos, no solo sobre el número de fills.

</details>

<details><summary>Ayuda</summary>

Usa engine_class en la primera ejecución; comparar la referencia consigo misma no contrasta tu respuesta.

</details>

### 6C · Dos órdenes sobre el mismo estado

**Dónde:** `main.py`, comentario `Lectura 6C`. No hay código pendiente aquí.
Antes de ejecutar `python main.py --through 6C`, predice fills y asks finales de
dos MARKET BUY de 0.3 sobre un solo libro. Compáralas con dos compras sobre libros
nuevos. Explica qué mantiene cada experimento y por qué la segunda orden puede
tener otro precio. Intenta la predicción antes de consultar 6C en la solución.
Comprueba consumo acumulado; no simula prioridad de colas ni eventos entre fotos.

<details><summary>Contrastar después de la predicción</summary>

En un mismo libro la primera compra toma 0.3 a 101; la segunda toma el 0.1 restante a 101 y 0.2 a 102. Queda ask102×1.4. Si reconstruyes antes de cada orden, ambas pagan 101: comparas escenarios independientes, no consumo sucesivo.

</details>

## Ejercicio 7 · Variantes — OPTIONAL

No son requisito para continuar ni para completar el principal.

### 7A · Invierte el lado

**Dónde:** `opcionales.py` / `practice`.

**Encargo:** OPTIONAL: vende 0.5 a mercado sobre sell_book y guarda sold para observar caja y bid restante.

**OPTIONAL: no necesario para continuar ni para evaluar lo requerido.**

Crea y conserva `sell_book = fresh_book()`. Envía sobre **ese libro** una MARKET de venta de 0.5 con tu PlannedEngine y guarda los fills en `sold`. Predice precio, signo de caja y bid restante; la observación consulta `sold` y `sell_book`. Al repetir la respuesta crea otra vez el libro para partir de la misma liquidez.

**Comprobación:** `python opcionales.py --through 7A`.

<details><summary>Contrastar después del intento</summary>

`[(99,0.5)]`; caja `49.5`, bid restante `0.5`.

No hace falta otra implementación para el lado sell.

</details>

<details><summary>Ayuda</summary>

Una venta consume bids y aporta caja.

</details>

### 7B · Dos tamaños caben en el mismo nivel

**Dónde:** `opcionales.py` / `practice`.

**Encargo:** OPTIONAL: compara compras MARKET de 0.1 y 0.2 en libros nuevos y guarda same_prices.

**OPTIONAL: no necesario para continuar ni para evaluar lo requerido.**

Calcula same_prices para compras MARKET de 0.1 y 0.2, siempre sobre una copia nueva. Usa la suma ponderada de los fills y predice si el precio cambia.

**Comprobación:** `python opcionales.py --through 7B`.

<details><summary>Contrastar después del intento</summary>

`[101.0,101.0]`. Más tamaño no empeora estrictamente el precio si sigue cabiendo.

Un empeoramiento requiere llegar a precios peores; compara siempre el mismo estado inicial.

</details>

<details><summary>Ayuda</summary>

El primer ask tiene 0.4 unidades; ambas cantidades caben ahí.

</details>

### 7C · Traza un proceso sin duplicarlo

**Dónde:** `opcionales.py` / `trace_process`.

**Encargo:** OPTIONAL: devuelve fills, pendiente y aceptación reutilizando las mismas fases; FOK rechazada no confirma.

**OPTIONAL: no necesario para continuar ni para evaluar lo requerido.**

Define trace_process para devolver (fills,remaining,accepted) usando las mismas fases del principal. En FOK rechazada devuelve antes de commit; solo LIMIT descansa. Contrasta cada resultado con PlannedEngine.

**Comprobación:** `python opcionales.py --through 7C`.

<details><summary>Contrastar después del intento</summary>

MARKET produce dos fills; LIMIT e IOC uno; FOK ninguno y accepted=False. Solo cambian validación y remanente.

La extensión hace visibles las fases y conserva un único algoritmo de planificación.

</details>

<details><summary>Ayuda</summary>

Reutiliza helpers; no escribas cuatro bucles de consumo.

</details>

### 7D · Tamaño y precio en el CSV

**Dónde:** `opcionales.py` / `practice`.

**Encargo:** OPTIONAL: calcula eff_prices para MARKET 0.1, 1 y 5 sobre copias nuevas de la fila sintética.

**OPTIONAL: no necesario para continuar ni para evaluar lo requerido.**

Para tamaños 0.1, 1.0 y 5.0 calcula eff_prices sobre la misma fila sintética reconstruida cada vez con SnapshotBook. Usa PlannedEngine; compara igualdad o empeoramiento, sin exigir crecimiento estricto.

**Comprobación:** `python opcionales.py --through 7D`.

<details><summary>Contrastar después del intento</summary>

Precios `100021.8`, `100021.8`, `100026.655162`: los dos primeros tamaños caben en el mismo nivel.

El experimento aísla tamaño manteniendo constante la foto inicial.

</details>

<details><summary>Ayuda</summary>

Reconstruye antes de cada tamaño para evitar confundir tamaño con liquidez ya consumida.

</details>

## Cierre

`python main.py` demuestra plan sin mutación, fills y niveles finales, las cuatro
políticas, costes y contraste. Explica con tus palabras por qué FOK rechazada
conserva ambos lados del libro. El consumidor llamará al mismo process: no necesita
conocer las fases internas. La siguiente lesson incluye sus propias bases.
