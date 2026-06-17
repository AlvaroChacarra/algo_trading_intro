# Clase 13 — Market making — Intro

> El otro lado del mercado: en vez de cruzar, cotizas bid y ask y ganas el spread. Pero acumulas inventario, y el inventario es riesgo. Skew por inventario como primera defensa.

## Contexto teórico

El otro lado del mercado: el **market maker** cotiza bid y ask y gana el **spread**. Su
enemigo es el **inventario**: si el flujo es desequilibrado acumula posición justo cuando el
mercado va en su contra (**adverse selection**).

Aparece la **utilidad CARA** `-e^{-γW}` y el parámetro de **aversión al riesgo** γ. La primera
defensa es el **skew por inventario**: el *reservation price* = `mid - skew·inventario` baja
ambas cotizaciones cuando estás largo, para que te compren menos y te vendan más y vuelvas a
plano.

## Qué construyes hoy

**MarketMaker: cotizar a ambos lados y gestionar inventario**

`exchange/strategies/market_maker.py` (`MarketMaker`): `quotes(book) -> (bid, ask)` en torno
al `reservation_price`, `on_fill` actualiza el inventario interno. Y `exchange/simulation.py`
(`MMSimulation`): como una limit no se cruza en el replay de snapshots, el market making se
simula contra un mid en paseo aleatorio con **modelo de intensidad de fills**
`λ(δ) = A·e^{-κδ}` (más cerca del mid, más probable que te ejecuten).

## Ejercicios de construcción

- **1. Cotiza alrededor del mid** — MarketMaker.quotes
- **2. El skew baja las cotizaciones si estás largo** — inventario -> reservation price
- **3. Reservation price** — centro de las cotizaciones
- **4. Simula al market maker** — MMSimulation

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/13_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/13_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> El market maker gana el spread, pero su enemigo es el inventario: cotiza para volver a plano.
