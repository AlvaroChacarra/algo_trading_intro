# Clase 5 — OOP II — OrderBook y PositionTracker (guía de implementación)

Pieza del framework: **clases OrderBook y PositionTracker (composición)**.

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

Composición explícita: `OrderBook` contiene `Level`; `PositionTracker.apply_fill` consume
objetos `Fill` de L3. Aquí el alumno *ve* a los objetos hablándose entre sí — el objetivo
declarado del curso.

El deck a medida (Pyodide) trae un inspector del `OrderBook` (métricas como properties) y un widget
del `PositionTracker` (pulsas fills y ves cash/posición/equity, con slider de mark). El núcleo
son 6 ejercicios que culminan en "los dos objetos, juntos"; el `.py` entregable es `book_demo.py`.
Puente: ya creas (L4) y compones (L5) objetos; falta la última pieza de OOP — compartir un
esqueleto entre muchos objetos: herencia (L6).

## Presentación (3 bloques)

1. **Un objeto que contiene objetos** — El OrderBook guarda dos listas (bids y asks). Las funciones de L2 se mudan al objeto: las métricas sin argumentos son propiedades (`book.spread`, `book.mid`); `imbalance(levels)` sigue siendo método porque recibe una decisión de profundidad.
2. **Estado interno y encapsulación** — El PositionTracker guarda _cash y _position con guión bajo: 'no me toques desde fuera, usa mis métodos'. apply_fill recibe un objeto Fill y actualiza el estado.
3. **Los objetos colaboran** — tracker.apply_fill(fill): el tracker no sabe de precios sueltos, sabe de Fills. equity(mark) marca el inventario a mercado. Cada pieza tiene una responsabilidad.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `05_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
