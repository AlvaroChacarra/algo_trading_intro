# Clase 8 — Órdenes y matching

> Enviar órdenes contra el libro y ver cómo se cruzan. Market, limit, IOC y FOK: cada tipo cambia el coste, la probabilidad de ejecución y el riesgo.

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

**MatchingEngine: cómo se cruzan las órdenes**

`exchange/matching.py` (`MatchingEngine.process(order, book) -> list[Fill]`): recorre el lado
contrario, planifica el cruce, aplica FOK (todo-o-nada), consume liquidez (muta el libro) y
descansa el remanente de una LIMIT. Devuelve los `Fill` generados.

Conecta todo lo anterior: recibe `Order` (L3), opera sobre `OrderBook` (L4), produce `Fill`
(L3). Es la primera pieza con lógica de ramas no trivial.

## Ejercicios de construcción

- **1. Una market order se llena** — MatchingEngine + MARKET
- **2. Una limit cruza solo a su precio** — LIMIT + remanente
- **3. Una market crossing limit sí cruza** — limit marketable
- **4. FOK: todo o nada** — OrderType.FOK
- **5. Precio efectivo de una market** — vwap de los fills

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/08_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/08_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> La forma en que envías la orden decide tu coste: cruzar ya, o esperar barato y arriesgarte a no ejecutar.
