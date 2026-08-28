# Clase 9 — Construir Market y su API

> Construir el objeto que mantiene el índice temporal, reconstruye el OrderBook actual y delega cada orden al MatchingEngine.

## Contexto teórico

Una simulación de mercado = **estado** (el libro) + **dinámica** (el matching) +
**tiempo** (el loop). El **replay** reproduce snapshots históricos en orden; en cada instante
puedes enviar órdenes contra el libro de ese momento.

Llevar la cuenta en el tiempo es lo que distingue un cálculo puntual de una estrategia: se
acumulan fills en un `PositionTracker` y se marca el equity a cada paso, obteniendo la curva
de PnL. Modelo de simulación: el libro se reconstruye en cada snapshot, así que las órdenes
límite no persisten entre pasos (las estrategias que quieren persistencia re-cotizan).

## Qué construyes hoy

**Market: componer snapshots, OrderBook, MatchingEngine y tiempo**

`exchange/market.py` (`Market`): `step()` reconstruye el libro desde el siguiente snapshot
y lo devuelve (o `None` al acabar); `submit(order)` cruza contra el libro actual vía el
`MatchingEngine`; `reset()` rebobina. Se compone con `PositionTracker` para seguir inventario
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L10.

## Ejercicios de construcción

- **B1 · Estado inicial** — __init__ y composición
- **B2 · Implementa step()** — cursor + factory de L7
- **B3 · Final de datos** — estado terminal explícito
- **B4 · submit() sin book: fail fast** — raise RuntimeError
- **B5 · Delega al MatchingEngine** — composición, no duplicación
- **B6 · reset()** — restaurar invariantes
- **B7 · Ahora sí: loop completo** — step hasta None
- **B8 · Challenge de integración** — step → submit → fills → tracker → equity

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/09_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/09_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Market añade tiempo y composición: step cambia el estado; submit delega la dinámica; reset vuelve al origen.
