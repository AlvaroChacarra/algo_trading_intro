# Clase 13 — Avellaneda-Stoikov I — El modelo (guía de implementación)

Pieza del framework: **AvellanedaStoikov: reservation price y optimal spread**.

## Teoría que cubre

**Avellaneda-Stoikov (2008)** sustituye el skew heurístico por el óptimo. Sale de maximizar
utilidad CARA sobre la riqueza final con inventario incierto; la solución (vía la ecuación
HJB de control óptimo estocástico — no hace falta derivarla) da dos fórmulas cerradas:

- **Reservation price**: `r = s − q·γ·σ²·(T−t)` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ²·(T−t) + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).

## Implementación técnica

`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
contador `_t` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
se enchufa al mismo `MMSimulation`. Demuestra herencia + especialización.

## Presentación (3 bloques)

1. **De dónde sale el modelo** — Maximizas utilidad CARA sobre tu riqueza final con inventario incierto. La solución (vía HJB) da dos fórmulas cerradas. No hace falta derivarlas para usarlas.
2. **Reservation price** — Es el mid ajustado por inventario y tiempo: largo de inventario y lejos del cierre -> bajas el centro para soltar. Cerca del cierre, el ajuste se apaga.
3. **Optimal spread** — Cuánto separas tus cotizaciones del reservation price. Crece con la aversión (gamma) y la volatilidad; depende de la liquidez (kappa).

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `13_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
