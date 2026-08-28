# Clase 14 — Avellaneda-Stoikov — modelo y simulación (guía de implementación)

Pieza del framework: **AvellanedaStoikov: reservation price, optimal spread y barridos de gamma**.

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

1. **De dónde sale el modelo** — Maximizas utilidad CARA sobre tu riqueza final con inventario incierto. La solución (vía HJB) da dos fórmulas cerradas.
2. **Reservation price y optimal spread** — r es el mid ajustado por inventario y tiempo; d es cuánto separas las cotizaciones. Al cierre, el ajuste por inventario se apaga.
3. **Simular y barrer gamma** — MMSimulation mueve el mid y te ejecuta según la distancia. Más gamma controla mejor el inventario, pero captura menos spread. No hay free lunch.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `14_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
