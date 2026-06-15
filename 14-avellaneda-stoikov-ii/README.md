# Clase 14 — Avellaneda-Stoikov II — Simulación

> Poner el modelo a correr: simular el market maker A-S contra un mid que se mueve, ver cómo controla el inventario, y barrer gamma para entender el trade-off riesgo/PnL.

## Contexto teórico

Poner el modelo a correr. Frente a un market maker naive, el A-S **controla el inventario**
mucho mejor: el reservation price lo empuja a soltar antes de cargar demasiado.

El **barrido de γ** muestra el trade-off sin atajos: más aversión inclina más el reservation
price y reduce el inventario máximo, pero al cotizar más defensivo captura menos spread (menos
PnL). No hay free lunch — esa es la intuición que se lleva el alumno. El cierre del bloque es
que el alumno **escribe su propia estrategia** y la enchufa al simulador.

## Qué construyes hoy

**simular A-S y barrer parámetros**

`MMSimulation(strategy, steps, A, kappa, sigma)` → `SimResult(mid, inventory, pnl)` con
`final_pnl` y `max_inventory`. Ejercicios de comparación: skew vs no-skew (determinista, misma
semilla), magnitud del reservation price vs γ. Auxiliar: subclasear `MarketMaker` (p.ej.
`FlatMaker`) y simularlo — el alumno cierra el círculo escribiendo y enchufando lo suyo.

## Ejercicios de construcción

- **1. Simula el A-S** — MMSimulation con A-S
- **2. El skew reduce el inventario** — comparar con / sin skew
- **3. Más gamma, más inclina el reservation price** — trade-off riesgo/PnL

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/14_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/14_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> Más gamma = más miedo al inventario: cotizas más defensivo, cargas menos posición, pero capturas menos spread.
