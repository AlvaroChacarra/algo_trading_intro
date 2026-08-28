# Clase 14 — Avellaneda-Stoikov — modelo y simulación

> Sustituir el skew heurístico por el resultado del modelo de Avellaneda-Stoikov (reservation price + optimal spread), y ponerlo a correr: simular, ver cómo controla el inventario y barrer gamma.

## Contexto teórico

**Avellaneda-Stoikov (2008)** sustituye el skew heurístico por el óptimo. Sale de maximizar
utilidad CARA sobre la riqueza final con inventario incierto; la solución (vía la ecuación
HJB de control óptimo estocástico — no hace falta derivarla) da dos fórmulas cerradas:

- **Tiempo normalizado**: `τ = (T−t)/T`, por tanto `τ ∈ [0,1]`.
- **Reservation price**: `r = s − q·γ·σ²·τ` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ²·τ + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).

## Qué construyes hoy

**AvellanedaStoikov: reservation price, optimal spread y barridos de gamma**

`exchange/strategies/avellaneda_stoikov.py` introduce por primera vez en L14
`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
reloj público `time` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
se enchufa al mismo `MMSimulation`. Demuestra herencia + especialización.

## Ejercicios de construcción

- **1. Reservation price con inventario** — fórmula r
- **2. Optimal spread positivo** — fórmula d
- **3. Cotizaciones A-S** — quotes simétricas en torno a r
- **4. Inventario inclina el centro** — A-S vs naive
- **5. Simula el A-S** — MMSimulation con A-S
- **6. El skew reduce el inventario** — comparar con / sin skew
- **7. Más gamma, más inclina el reservation price** — trade-off riesgo/PnL

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/14_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/14_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> El reservation price inclina según inventario y tiempo; el optimal spread cobra por el riesgo. Más gamma = más defensivo, menos inventario, menos PnL.
