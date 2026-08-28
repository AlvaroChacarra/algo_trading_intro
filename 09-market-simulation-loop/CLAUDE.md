# Clase 9 — Construir Market y su API (guía de implementación)

Pieza del framework: **Market: componer snapshots, OrderBook, MatchingEngine y tiempo**.

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
y equity. Es el andamiaje sobre el que se monta el `Backtest` en L10.

## Presentación (3 bloques)

1. **El estado de Market** — Market contiene snapshots, profundidad, índice, book actual y un MatchingEngine. Antes del primer tick: _i=-1 y book=None.
2. **step() cambia el tiempo y el estado** — Avanza el cursor y reconstruye book con OrderBook.from_snapshot. Al agotarse los datos deja book=None.
3. **submit() delega; reset() restaura** — Market no reprograma matching: verifica que hay book y delega. reset restaura exactamente el estado previo al primer tick.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `09_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L9. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
