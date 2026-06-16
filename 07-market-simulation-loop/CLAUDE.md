# Clase 7 — El loop de simulación (guía de implementación)

Pieza del framework: **Market: reproducir snapshots y ejecutar en el tiempo**.

## Teoría que cubre

Una simulación de mercado = **estado** (el libro) + **dinámica** (el matching) +
**tiempo** (el loop). El **replay** reproduce snapshots históricos en orden; en cada instante
puedes enviar órdenes contra el libro de ese momento.

Llevar la cuenta en el tiempo es lo que distingue un cálculo puntual de una estrategia: se
acumulan fills en un `PositionTracker` y se marca el equity a cada paso, obteniendo la curva
de PnL. Modelo de simulación: el libro se reconstruye en cada snapshot, así que las órdenes
límite no persisten entre pasos (las estrategias que quieren persistencia re-cotizan).

## Implementación técnica

`exchange/market.py` (`Market`): `step()` reconstruye el libro desde el siguiente snapshot
y lo devuelve (o `None` al acabar); `submit(order)` cruza contra el libro actual vía el
`MatchingEngine`; `reset()` rebobina. Se compone con `PositionTracker` para seguir inventario
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L8.

## Presentación (3 bloques)

1. **step() avanza el tiempo** — Market.step() reconstruye el libro desde el siguiente snapshot y lo devuelve. Cuando se acaban, devuelve None. Ese es tu reloj.
2. **submit() ejecuta contra el libro actual** — En cada paso puedes enviar una orden: m.submit(order) la cruza contra el libro de ese instante y te devuelve los fills.
3. **PositionTracker lleva la cuenta** — Aplicas cada fill al tracker y en cualquier momento consultas equity(mid). Esa es tu curva de PnL.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `07_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
