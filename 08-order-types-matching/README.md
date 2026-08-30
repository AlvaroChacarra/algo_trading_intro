# Clase 8 — Construir MatchingEngine

> Programar el algoritmo que convierte Order + OrderBook en fills y estado nuevo, reutilizando un único proceso para MARKET, LIMIT, IOC y FOK.

## Contexto teórico

El **matching** convierte el libro de foto estática en mercado con dinámica. Prioridad
precio-tiempo: una orden entrante consume primero los mejores niveles del lado contrario.

Tipos de orden y su trade-off **coste / certeza / riesgo**:
- **MARKET**: cruza al precio que haga falta; segura pero paga **slippage** al barrer niveles.
- **LIMIT**: solo cruza a tu precio o mejor; barata pero el resto descansa (incierta).
- **IOC** (immediate-or-cancel): cruza lo que pueda, cancela el resto.
- **FOK** (fill-or-kill): todo o nada.

El **precio efectivo** de una market es el VWAP de sus fills, peor que el best ask cuanto más grande.

## Qué construyes hoy

**MatchingEngine: planificar cruces, validar y mutar el libro**

`exchange/matching.py` (`MatchingEngine.process(order, book) -> list[Fill]`): valida primero
que `order.symbol == book.symbol`, recorre el lado contrario, planifica el cruce, aplica FOK
(todo-o-nada), consume liquidez (muta el libro) y descansa el remanente de una LIMIT. Devuelve
los `Fill` generados.

Conecta todo lo anterior: recibe `Order` (L4), opera sobre `OrderBook` (L5), produce `Fill`
(L4). La separación PLAN → VALIDATE → COMMIT hace atómica una FOK fallida.

## Ejercicios de construcción

- **B1 · ¿Qué lado consumo?** — selección BUY/SELL
- **B2 · remaining + take** — planificar sin mutar
- **B3 · Primera MARKET completa** — loop → reduce → Fill
- **B4 · Diseña _crosses()** — LIMIT simétrica BUY/SELL
- **B5 · LIMIT marketable** — detener el plan en el límite
- **B6 · El remanente LIMIT descansa** — book.add_limit
- **B7 · Diseña IOC sin duplicar el engine** — misma ejecución, otra política de remanente
- **B8 · Depura FOK: plan → validate → commit** — atomicidad del estado
- **B9 · Refactor: un único process()** — MARKET/LIMIT/IOC/FOK reutilizando fases
- **B10 · Prueba contra la referencia** — differential testing

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/08_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/08_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Cuando una operación puede abortarse, primero planifica y valida; después muta el estado.
