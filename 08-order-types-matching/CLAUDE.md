# Clase 8 — Construir MatchingEngine (guía de implementación)

Pieza del framework: **MatchingEngine: planificar cruces, validar y mutar el libro**.

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

Conecta todo lo anterior: recibe `Order` (L4), opera sobre `OrderBook` (L5), produce `Fill`
(L4). La separación PLAN → VALIDATE → COMMIT hace atómica una FOK fallida.

## Presentación (3 bloques)

1. **Seleccionar y planificar** — BUY consume asks y SELL consume bids. remaining y take permiten recorrer niveles sin mutar todavía.
2. **Validar y hacer commit** — FOK obliga a separar PLAN de COMMIT: si no cabe entera, el libro debe quedar idéntico.
3. **Un algoritmo, cuatro políticas** — MARKET, LIMIT, IOC y FOK comparten selección, planificación y commit. Solo cambian el cruce permitido y el tratamiento del remanente.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `08_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
