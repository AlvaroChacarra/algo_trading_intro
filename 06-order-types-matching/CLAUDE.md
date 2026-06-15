# Clase 6 — Órdenes y matching (guía de implementación)

Pieza del framework: **MatchingEngine: cómo se cruzan las órdenes**.

## Teoría que cubre

El **matching** convierte el libro de foto estática en mercado con dinámica. Prioridad
precio-tiempo: una orden entrante consume primero los mejores niveles del lado contrario.

Tipos de orden y su trade-off **coste / certeza / riesgo**:
- **MARKET**: cruza al precio que haga falta; segura pero paga **slippage** al barrer niveles.
- **LIMIT**: solo cruza a tu precio o mejor; barata pero el resto descansa (incierta).
- **IOC** (immediate-or-cancel): cruza lo que pueda, cancela el resto.
- **FOK** (fill-or-kill): todo o nada.

El **precio efectivo** de una market es el VWAP de sus fills, peor que el best ask cuanto más grande.

## Implementación técnica

`exchange/matching.py` (`MatchingEngine.process(order, book) -> list[Fill]`): recorre el lado
contrario, planifica el cruce, aplica FOK (todo-o-nada), consume liquidez (muta el libro) y
descansa el remanente de una LIMIT. Devuelve los `Fill` generados.

Conecta todo lo anterior: recibe `Order` (L3), opera sobre `OrderBook` (L4), produce `Fill`
(L3). Es la primera pieza con lógica de ramas no trivial.

## Presentación (3 bloques)

1. **El motor de cruce** — MatchingEngine.process(order, book) recorre el lado contrario, consume liquidez y devuelve los fills. El libro queda modificado.
2. **Market vs limit** — Una market cruza al precio que haga falta hasta llenarse (caro pero seguro). Una limit solo cruza a tu precio o mejor; el resto descansa (barato pero incierto).
3. **IOC y FOK** — IOC cruza lo que pueda y cancela el resto (nada descansa). FOK es todo-o-nada: si no se llena entera, no se ejecuta nada.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = ej. 1-3 (en clase), **Si vamos bien** = resto, **Auxiliares** = cuaderno `06_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
