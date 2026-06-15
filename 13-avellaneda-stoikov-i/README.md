# Clase 13 — Avellaneda-Stoikov I — El modelo

> Sustituir el skew heurístico por el resultado del modelo de Avellaneda-Stoikov: un reservation price y un optimal spread que salen de maximizar utilidad bajo riesgo de inventario.

## Contexto teórico

**Avellaneda-Stoikov (2008)** sustituye el skew heurístico por el óptimo. Sale de maximizar
utilidad CARA sobre la riqueza final con inventario incierto; la solución (vía la ecuación
HJB de control óptimo estocástico — no hace falta derivarla) da dos fórmulas cerradas:

- **Reservation price**: `r = s − q·γ·σ²·(T−t)` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ²·(T−t) + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).

## Qué construyes hoy

**AvellanedaStoikov: reservation price y optimal spread**

`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
contador `_t` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
se enchufa al mismo `MMSimulation`. Demuestra herencia + especialización.

## Ejercicios de construcción

- **1. Reservation price con inventario** — fórmula r
- **2. Optimal spread positivo** — fórmula d
- **3. Cotizaciones A-S** — quotes simétricas en torno a r
- **4. Inventario inclina el centro** — A-S vs naive

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/13_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/13_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> El reservation price inclina tus cotizaciones según inventario y tiempo; el optimal spread fija cuánto cobras por el riesgo.
