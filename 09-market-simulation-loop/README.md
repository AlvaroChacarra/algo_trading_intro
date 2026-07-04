# Clase 9 — El loop de simulación

> Poner el tiempo en marcha: recorrer los snapshots, enviar órdenes en cada paso y llevar la cuenta de caja, inventario y equity con PositionTracker.

## Contexto teórico

Una simulación de mercado = **estado** (el libro) + **dinámica** (el matching) +
**tiempo** (el loop). El **replay** reproduce snapshots históricos en orden; en cada instante
puedes enviar órdenes contra el libro de ese momento.

Llevar la cuenta en el tiempo es lo que distingue un cálculo puntual de una estrategia: se
acumulan fills en un `PositionTracker` y se marca el equity a cada paso, obteniendo la curva
de PnL. Modelo de simulación: el libro se reconstruye en cada snapshot, así que las órdenes
límite no persisten entre pasos (las estrategias que quieren persistencia re-cotizan).

## Qué construyes hoy

**Market: reproducir snapshots y ejecutar en el tiempo**

`exchange/market.py` (`Market`): `step()` reconstruye el libro desde el siguiente snapshot
y lo devuelve (o `None` al acabar); `submit(order)` cruza contra el libro actual vía el
`MatchingEngine`; `reset()` rebobina. Se compone con `PositionTracker` para seguir inventario
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L8.

## Ejercicios de construcción

- **1. Cuenta los pasos** — el loop step()
- **2. Ejecuta una orden en un paso** — submit
- **3. Acumula posición en el tiempo** — loop + tracker
- **4. Equity final** — marcar a mercado

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/09_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/09_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Mercado = estado (libro) + dinámica (matching) + tiempo (el loop). Todo junto, ya simulas.
