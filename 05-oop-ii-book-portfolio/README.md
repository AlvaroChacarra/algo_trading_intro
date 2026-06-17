# Clase 5 — OOP II — OrderBook y PositionTracker

> Construir el libro como objeto que contiene niveles, con métricas como métodos. Y un PositionTracker que consume objetos Fill. Aquí ves cómo los objetos se entrelazan.

## Contexto teórico

Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por métodos). El `OrderBook` contiene niveles de precio y
expone métricas como métodos. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.

## Qué construyes hoy

**clases OrderBook y PositionTracker (composición)**

`exchange/book.py` (`OrderBook`, `Level`) con bids ordenados desc y asks asc, y métodos
`best_bid/best_ask/spread/mid/imbalance`. `exchange/portfolio.py` (`PositionTracker`) con
`_cash`/`_position` privados, `apply_fill(fill)` y `equity(mark)`.

Composición explícita: `OrderBook` contiene `Level`; `PositionTracker.apply_fill` consume
objetos `Fill` de L3. Aquí el alumno *ve* a los objetos hablándose entre sí — el objetivo
declarado del curso.

## Ejercicios de construcción

- **1. OrderBook con niveles** — atributos que son listas
- **2. best_bid / best_ask / spread / mid** — métodos sobre estado
- **3. Imbalance del nivel 1** — método con cálculo
- **4. PositionTracker** — estado privado
- **5. Equity a mercado** — componer estado

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/05_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/05_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Composición: un OrderBook contiene niveles; un PositionTracker consume Fills. Los objetos se hablan entre sí.
