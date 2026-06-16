# Clase 14 — Avellaneda-Stoikov II — Simulación (guía de implementación)

Pieza del framework: **simular A-S y barrer parámetros**.

## Teoría que cubre

Poner el modelo a correr. Frente a un market maker naive, el A-S **controla el inventario**
mucho mejor: el reservation price lo empuja a soltar antes de cargar demasiado.

El **barrido de γ** muestra el trade-off sin atajos: más aversión inclina más el reservation
price y reduce el inventario máximo, pero al cotizar más defensivo captura menos spread (menos
PnL). No hay free lunch — esa es la intuición que se lleva el alumno. El cierre del bloque es
que el alumno **escribe su propia estrategia** y la enchufa al simulador.

## Implementación técnica

`MMSimulation(strategy, steps, A, kappa, sigma)` → `SimResult(mid, inventory, pnl)` con
`final_pnl` y `max_inventory`. Ejercicios de comparación: skew vs no-skew (determinista, misma
semilla), magnitud del reservation price vs γ. Auxiliar: subclasear `MarketMaker` (p.ej.
`FlatMaker`) y simularlo — el alumno cierra el círculo escribiendo y enchufando lo suyo.

## Presentación (3 bloques)

1. **Simular para entender** — MMSimulation mueve el mid con un paseo aleatorio y te ejecuta según la distancia de tus cotizaciones. Ves la senda de inventario y el PnL marcado a mercado.
2. **A-S controla el inventario** — Frente a un market maker naive, el A-S mantiene el inventario mucho más cerca de 0: el reservation price lo empuja a soltar antes de cargar demasiado.
3. **El barrido de gamma** — gamma es la perilla de aversión. Súbela y el inventario máximo baja, pero también las vueltas (menos PnL). Bájala y pasa lo contrario. No hay free lunch.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `14_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
