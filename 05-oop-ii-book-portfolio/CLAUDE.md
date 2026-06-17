# Clase 5 — OOP II — OrderBook y PositionTracker (guía de implementación)

Pieza del framework: **clases OrderBook y PositionTracker (composición)**.

## Teoría que cubre

Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por métodos). El `OrderBook` contiene niveles de precio y
expone métricas como métodos. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.

## Implementación técnica

`exchange/book.py` (`OrderBook`, `Level`) con bids ordenados desc y asks asc, y métodos
`best_bid/best_ask/spread/mid/imbalance`. `exchange/portfolio.py` (`PositionTracker`) con
`_cash`/`_position` privados, `apply_fill(fill)` y `equity(mark)`.

Composición explícita: `OrderBook` contiene `Level`; `PositionTracker.apply_fill` consume
objetos `Fill` de L3. Aquí el alumno *ve* a los objetos hablándose entre sí — el objetivo
declarado del curso.

## Presentación (3 bloques)

1. **Un objeto que contiene objetos** — El OrderBook guarda dos listas (bids y asks). Esas cinco funciones de la clase 2 que recibían book ahora son métodos: book.spread(), book.mid().
2. **Estado privado y encapsulación** — El PositionTracker guarda _cash y _position con guión bajo: 'no me toques desde fuera, usa mis métodos'. apply_fill recibe un objeto Fill y actualiza el estado.
3. **Los objetos colaboran** — tracker.apply_fill(fill): el tracker no sabe de precios sueltos, sabe de Fills. equity(mark) marca el inventario a mercado. Cada pieza tiene una responsabilidad.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `05_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
