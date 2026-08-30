# Clase 5 — OOP II — OrderBook y PositionTracker

> Construir un libro didáctico que contiene niveles, estabilizar las métricas sin argumentos como propiedades y migrar después a la firma pública de OrderBook sin un cambio silencioso.

## Contexto teórico

Dos ideas de diseño: **composición** (un objeto contiene otros) y **encapsulación**
(estado interno que se toca solo por su API). El `OrderBook` contiene niveles de precio y
expone las métricas sin argumentos como properties estables. El `PositionTracker` es una pequeña máquina de estado: parte de
caja y posición a cero y las actualiza con cada `Fill`.

El concepto financiero clave es **equity** = `cash + position · mark_price`: tu valor total
marcando el inventario al precio actual de mercado. Es la fotografía de PnL que se usará en
todos los backtests.

## Qué construyes hoy

**OrderBookMini + PositionTracker; migración explícita al OrderBook estable de exchange**

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
