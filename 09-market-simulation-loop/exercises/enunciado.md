# Lesson 9 · Dale un reloj a tu mercado

**Objetivo.** Construir `ReplayMarket` para visitar fotos en orden, ejecutar en la actual y volver al inicio. El libro cambia con cada foto; caja y posición pertenecen a una cartera externa.

Todo está en esta carpeta. Edita `market.py` y `main.py`; ejecuta `python main.py` desde `exercises`. Sin completar nada verás el escenario y «Completa 1A en market.py». Al resolver cada apartado usa `--through 1A`, `--through 1B`… para detenerte antes de los huecos posteriores. Trabaja con instancias nuevas tras editar clases; conserva tus intentos antes de consultar soluciones.

| Archivo | Papel |
|---|---|
| `market.py` | **Nuevo:** reloj, libro activo y delegación. |
| `main.py` | **A completar:** recorrido, elección del instante y observaciones. |
| `base_book.py`, `adapters.py`, `book.py` | **Incluidos:** consultas y factory desde las fuentes canónicas de L5/L7. |
| `matching.py` | **Incluido:** PlannedEngine y sus funciones desde el Markdown canónico de L8. |
| `portfolio.py` | **Incluido:** PositionTracker desde el Markdown canónico de L5. |
| `scenarios.py` | **Proporcionado:** dos fotos de control y firmas para la referencia de matching. |
| `exchange/` | **Proporcionado:** Order/OrderType/Side, ExecutionFill, CSV y API tipada de consulta. No sustituye tus clases locales. |
| `opcionales.py` | Variantes OPTIONAL; el principal funciona sin completarlas. |
| `solutions/solucion.md` | Un bloque completo por archivo con el encargo comentado y la solución debajo. |

**Contratos incluidos.** `SnapshotBook.from_snapshot(symbol,row,depth)` crea un objeto nuevo con bids/asks y consultas mid/spread. `PlannedEngine.process(order,book,timestamp=None)` consume la liquidez de ese libro y devuelve fills. `PositionTracker(1000)` empieza con caja 1000 y posición cero; `apply_fill(fill)` registra ejecución y `equity(mid)` solo valora. `Order(symbol,side,size,price=None,order_type=...)` normaliza buy/sell; cada ExecutionFill contiene order_id, symbol, side, price, size y timestamp, y conserva `cash_flow()`. Se registra cada fill, no la intención enviada.

**Datos y alcance.** Dos fotos sintéticas de control: precios USD/BTC, tamaños BTC, timestamp 0/1. El CSV local contiene 500 fotos sintéticas BTCUSDT, diez niveles por lado; precios USDT/BTC, tamaños BTC y timestamps en segundos Unix. DictReader entrega texto; la factory incluida lo adapta. Procedencia y campos en `exchange/_data/README.md`. No es el JSON histórico real de L7. Caja inicial 1000 en los dos experimentos, sin comisiones ni restricción de financiación: la compra del CSV puede dejar caja negativa. Al avanzar se sustituye el libro; no hay cola de órdenes pasivas ni ejecución entre fotos.

**Autonomía.** El ciclo de vida se guía en el ejercicio 1. En los bucles de 2B y 3B decide tú qué conservar y cuándo registrar los datos. Antes de ejecutar 4B escribe tu predicción; después explica el resultado con lo que observas.

## Ejercicio 1 · Construye el reloj — LIVE

### 1A · Inicializa el reloj

**Dónde:** `market.py` / `ReplayMarket.__init__`.

**Encargo:** Guarda rows como lista, symbol, depth y PlannedEngine; deja _i=-1 y book=None.

Crea el estado anterior a la primera foto. El constructor recibe rows, symbol="BTC" y depth=10; materializa rows, conserva la configuración y crea un PlannedEngine. No actives todavía una foto. timestamp ya está proporcionado.

**Comprobación:** `python main.py --through 1A`.

<details><summary>Contrastar después del intento</summary>

-1 None; cada instancia conserva su propio cursor y motor.

</details>

### 1B · Entrega la siguiente foto

**Dónde:** `market.py` / `ReplayMarket.step`.

**Encargo:** Avanza _i una vez; devuelve un SnapshotBook nuevo o limpia book y devuelve None al agotarse.

Implementa step sin interpretar otra vez las columnas: incrementa _i una vez, detecta el final y delega SnapshotBook.from_snapshot(self.symbol, self.rows[self._i], self.depth). Guarda y devuelve el nuevo objeto. Para una entrada vacía y al agotar devuelve None y book=None.

**Comprobación:** `python main.py --through 1B`.

<details><summary>Contrastar después del intento</summary>

0 100.0 0; repetir step con datos agotados mantiene book=None.

</details>

### 1C · Ejecuta sin mover el reloj

**Dónde:** `market.py` / `ReplayMarket.submit`.

**Encargo:** Exige un libro activo y devuelve engine.process(order, book, timestamp), sin avanzar _i.

Predice cursor, caja y posición tras BUY 1 a MARKET. Sin foto, submit debe lanzar RuntimeError; con foto delega a engine.process con el timestamp actual. La observación de main aplica los fills a una cartera externa.

**Comprobación:** `python main.py --through 1C`.

<details><summary>Contrastar después del intento</summary>

cursor 0; cash 899; position 1; ask restante 2 y equity 999.

</details>

### 1D · Vuelve al origen

**Dónde:** `market.py` / `ReplayMarket.reset`.

**Encargo:** Restaura _i=-1 y book=None, conservando las filas y el motor.

Predice qué permanece al pasar a la segunda foto y al reiniciar solo el mercado. reset restaura el estado de 1A sin borrar rows, sustituir engine ni conocer una cartera. No hace falta recrear el motor.

**Comprobación:** `python main.py --through 1D`.

<details><summary>Contrastar después del intento</summary>

segunda foto: cursor 1, mid 102, equity 1001 y ask 3. Fin: None. Reset: -1/None; cartera 899/1.

</details>

## Ejercicio 2 · Ciclo de vida y recorrido — LIVE / REQUIRED

### 2A · Rechaza una orden sin foto

**Dónde:** `main.py` / `practice`.

**Encargo:** Intenta enviar antes del primer step, captura solo RuntimeError y guarda rejected=True.

En practice, captura únicamente RuntimeError al enviar una MARKET BUY antes del primer step. rejected debe indicar que el guard funcionó. Explica por qué se aplica también después del agotamiento.

**Comprobación:** `python main.py --through 2A`.

<details><summary>Contrastar después del intento</summary>

sin foto: True; una foto activa es la precondición de submit.

</details>

### 2B · Recorre y repite

**Dónde:** `main.py` / `mids_of`.

**Encargo:** Reinicia market, visita cada foto hasta None y devuelve sus mids en una lista.

Completa mids_of(market). Debe permitir recorrer dos veces el mismo objeto y devolver [] si está vacío. Diseña el bucle y captura cada mid mientras la foto siga activa. No copies el recorrido de trade_at.

**Comprobación:** `python main.py --through 2B`.

<details><summary>Contrastar después del intento</summary>

[100.0, 102.0] en ambos recorridos; vacío []. Al terminar ya no hay market.book.

</details>

## Ejercicio 3 · El instante importa — REQUIRED

### 3A · Conserva apertura y cierre

**Dónde:** `main.py` / `endpoints`.

**Encargo:** Usa mids_of para devolver el primer y último mid; si no hay fotos devuelve (None, None).

Devuelve (apertura,cierre) a partir de mids_of; la sesión vacía produce (None,None). Explica por qué consultas los valores guardados y no market.book al finalizar.

**Comprobación:** `python main.py --through 3A`.

<details><summary>Contrastar después del intento</summary>

(100.0, 102.0) y (None, None). No son libros persistentes.

</details>

### 3B · Elige cuándo comprar

**Dónde:** `main.py` / `trade_at`.

**Encargo:** Recorre todas las filas, compra una unidad solo en el índice at y devuelve fills, tracker y marks.

Implementa trade_at(rows, at, symbol="BTC"). Crea un ReplayMarket y un PositionTracker(1000), visita todas las fotos y compra exactamente una unidad solo cuando el índice activo sea at. Guarda el mid antes de enviar la orden; aplica cada fill confirmado y acumúlalo. Devuelve (fills, tracker, marks), con un mark por fila. Si at no existe no opera; si faltan filas devuelve listas vacías y cartera intacta. Elige tú la estructura del bucle.

**Comprobación:** `python main.py --through 3B`.

<details><summary>Contrastar después del intento</summary>

En índice 0: caja899 y equity final1001; en 1: caja897 y equity999; en9: posición0 y equity1000. Cambia el precio de ejecución, no el reloj.

</details>

## Ejercicio 4 · Otra entrada y un límite del modelo — REQUIRED

### 4A · Repite con el CSV

**Dónde:** `main.py` / `practice`.

**Encargo:** Lee csv_path con DictReader y usa trade_at en el índice 9 con symbol="BTCUSDT"; guarda los resultados de la sesión.

El csv_path está proporcionado en main. Lee con csv.DictReader, materializa session_rows y llama a tu trade_at en el índice 9 con symbol="BTCUSDT". Guarda session_fills, session_tracker y session_marks. Comprueba número de marks, símbolo de los fills y que la posición sea suma de tamaños ejecutados: la cantidad pedida no garantiza ejecución completa.

**Comprobación:** `python main.py --through 4A`.

<details><summary>Contrastar después del intento</summary>

500 marks. Position coincide con la cantidad ejecutada. Todos los fills pertenecen a BTCUSDT. El mismo reloj sirve para filas textuales.

</details>

### 4B · ¿Qué sobrevive a la próxima foto?

**Dónde:** `main.py` / `practice`.

**Encargo:** Envía LIMIT BUY 0.5 a 98 en la primera foto, aplica solo sus fills y observa bid98, cursor y cartera antes y después de step.

**Transferencia REQUIRED.** Antes de consultar la respuesta, escribe qué esperas que pase con un bid pasivo al llegar otra foto. En practice crea limit_market y limit_tracker(1000), avanza una vez y envía LIMIT BUY 0.5 a 98. Aplica solo limit_fills. Guarda pending_before/pending_after (si hay bid a98) y before/after como (cursor,cash,position) a ambos lados del siguiente step. Compara, explica y responde: ¿has simulado la ejecución de una orden pasiva persistente? Diseña la comprobación sin copiar una función resuelta.

**Comprobación:** `python main.py --through 4B`.

<details><summary>Contrastar después del intento</summary>

Cero fills; bid98 True→False; (0,1000,0)→(1,1000,0). Se reemplaza la foto; no hay una cola de órdenes que sobreviva ni datos de eventos entre fotos.

</details>

## Ejercicio 5 · Variantes voluntarias — OPTIONAL

### 5A · Entrada vacía

**Dónde:** `opcionales.py` / `optional`.

**Encargo:** Crea empty=ReplayMarket([]) y guarda dos step consecutivos en outputs.

Llama dos veces a step sobre una entrada vacía y predice su book.

**Comprobación:** `python opcionales.py` después de completar las variantes anteriores y el principal.

<details><summary>Contrastar después del intento</summary>

[None, None]; book=None.

</details>

### 5B · Dos experimentos desde limpio

**Dónde:** `opcionales.py` / `optional`.

**Encargo:** Ejecuta trade_at(rows, 0) dos veces y conserva sus carteras en first_run y second_run.

Ejecuta dos experimentos de compra en índice0. Cada trade_at crea mercado y cartera nuevos. Explica la diferencia con hacer solo market.reset.

**Comprobación:** `python opcionales.py` después de completar las variantes anteriores y el principal.

<details><summary>Contrastar después del intento</summary>

899/1 y899/1. Reiniciar solo el mercado conserva una cartera externa; no debe duplicarse la compra al comparar experimentos nuevos.

</details>

### 5C · Un calendario sencillo

**Dónde:** `opcionales.py` / `optional`.

**Encargo:** Recorre el CSV y pide BUY 0.1 cada 50 fotos hasta confirmar 1; acumula solo fills en executed y cuenta fotos en i.

Con el CSV, compra0.1 cada50 fotos hasta confirmar una unidad. Acumula solo lo ejecutado y cuenta todas las fotos, aunque ya no envíes órdenes. Esta extensión no es necesaria para el principal ni para L12.

**Comprobación:** `python opcionales.py` después de completar las variantes anteriores y el principal.

<details><summary>Contrastar después del intento</summary>

500 fotos y executed1.0. El calendario cuenta tiempo; los fills cuentan unidades.

</details>

### 5D · El acumulado fuera del trading

**Dónde:** `opcionales.py` / `optional`.

**Encargo:** Recorre lecturas, suma kWh en consumido y guarda el total de cada paso en curva.

lecturas[i] contiene consumo de una hora en kWh. Guarda el total y su curva acumulada. Al volver al trading, explica por qué una equity curve no suma todos los mids: valora una cartera en cada instante.

**Comprobación:** `python opcionales.py` después de completar las variantes anteriores y el principal.

<details><summary>Contrastar después del intento</summary>

[0.4,1.0,2.2,3.1,3.4,3.9]. Total3.9kWh; equity=cash+position×mid en cada foto, no acumulación de precios.

</details>
