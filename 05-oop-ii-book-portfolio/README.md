# Clase 5 — OOP II — OrderBook y PositionTracker

> Construir el libro como objeto que contiene niveles, con métricas sin argumentos estabilizadas como propiedades. Y un PositionTracker que consume objetos Fill. Aquí ves cómo los objetos se entrelazan.

## Contexto teórico

Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por su API). El `OrderBook` contiene niveles de precio y
expone las métricas sin argumentos como properties estables. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.

## Qué construyes hoy

**clases OrderBook y PositionTracker (composición)**

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

## Ejercicios de construcción

- **1. OrderBook: un objeto que contiene niveles** — composición
- **2. best_bid / best_ask / spread / mid** — @property sobre el estado
- **3. imbalance() del nivel 1** — otro método
- **4. PositionTracker: estado interno** — encapsulación + apply_fill
- **5. equity a mercado** — componer el estado
- **6. Los dos objetos, juntos** — composición end-to-end

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/05_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/05_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Composición: un OrderBook contiene niveles; un PositionTracker consume Fills. Los objetos se hablan entre sí.
