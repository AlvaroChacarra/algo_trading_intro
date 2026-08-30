# Clase 5 — OOP II — OrderBook y PositionTracker (guía de implementación)

Pieza del framework: **OrderBookMini + PositionTracker; migración explícita al OrderBook estable de exchange**.

## Teoría que cubre

Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por su API). El `OrderBook` contiene niveles de precio y
expone las métricas sin argumentos como properties estables. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.

## Implementación técnica

`exchange/book.py` (`OrderBook`, `Level`) con bids ordenados desc y asks asc;
`best_bid/best_ask/spread/mid` son properties e `imbalance(levels)` es método. `exchange/portfolio.py` (`PositionTracker`) con
`_cash`/`_position` como implementación interna, `apply_fill(fill)` y `equity(mark)`.

La construcción usa `OrderBookMini(bids, asks)` con tuplas para aislar composición y properties.
La migración se declara antes de usar el paquete: `OrderBook(symbol, bids: list[Level],
asks: list[Level])`. Las lecturas `best_bid`, `best_ask`, `spread`, `mid` siguen siendo properties
e `imbalance(levels)` sigue siendo método. `PositionTracker.apply_fill` consume el `Fill` estable
introducido en L4.

El documento HTML autocontenido trae un inspector del `OrderBook` (métricas como properties) y un widget
del `PositionTracker` (pulsas fills y ves cash/posición/equity, con slider de mark). El núcleo
son 6 ejercicios que culminan en "los dos objetos, juntos"; el `.py` entregable es `book_demo.py`.
Puente: ya creas (L4) y compones (L5) objetos; falta la última pieza de OOP — compartir un
esqueleto entre muchos objetos: herencia (L6).

## Presentación (3 bloques)

1. **Un objeto que contiene objetos** — OrderBookMini guarda dos listas de tuplas para aislar la idea de composición. Las funciones de L2 se mudan al objeto: las métricas sin argumentos son properties (`book.spread`, `book.mid`); `imbalance(levels)` sigue siendo método. Al final se migra al `OrderBook(symbol, bids: list[Level], asks: list[Level])` estable de exchange.
2. **Estado interno y encapsulación** — El PositionTracker guarda _cash y _position con guión bajo: 'no me toques desde fuera, usa mis métodos'. apply_fill recibe un objeto Fill y actualiza el estado.
3. **Los objetos colaboran** — tracker.apply_fill(fill): el tracker no sabe de precios sueltos, sabe de Fills. equity(mark) marca el inventario a mercado. Cada pieza tiene una responsabilidad.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `05_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L5. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
