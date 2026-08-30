# Clase 14 — Avellaneda-Stoikov — modelo y simulación (guía de implementación)

Pieza del framework: **AvellanedaStoikov: reservation price, optimal spread y barridos de gamma**.

## Teoría que cubre

**Avellaneda-Stoikov (2008)** sustituye el skew heurístico por el óptimo. Sale de maximizar
utilidad CARA sobre la riqueza final con inventario incierto; la solución (vía la ecuación
HJB de control óptimo estocástico — no hace falta derivarla) da dos fórmulas cerradas:

- **Tiempo normalizado**: `τ = clip((H−t)/H, 0, 1)`, por tanto `τ ∈ [0,1]` y no tiene unidades.
- **Volatilidad de horizonte**: `σ_H = std(S_H−S_0)`, en unidades de precio; la varianza
  que queda es `σ_H²·τ`.
- **Reservation price**: `r = s − q·γ·σ_H²·τ` — el mid ajustado por inventario `q` y tiempo.
- **Optimal spread**: `d = γ·σ_H²·τ + (2/γ)·ln(1 + γ/κ)` — cuánto separas tus cotizaciones.

Ledger de unidades: `s`, `r`, `d` y `σ_H` son precios; `q` cuenta unidades de inventario del
modelo; `γ` y `κ` son inversas de precio; `τ` es adimensional. Así los dos sumandos de `d`
y el desplazamiento `s−r` quedan expresados en precio, y `γ/κ` es adimensional.

Detalle clave: el ajuste por inventario **se apaga al acercarse el cierre** (`t → T`).

## Implementación técnica

`exchange/strategies/avellaneda_stoikov.py` introduce por primera vez en L14
`AvellanedaStoikov(MarketMaker)`: parámetros `gamma`, `sigma`, `kappa`, `horizon`; sobrescribe
`reservation_price` y añade `optimal_spread`, y `quotes` cotiza simétrico en torno a `r`. El
reloj público `time` avanza el tiempo. Al ser subclase de `MarketMaker`, hereda `on_fill`/inventario y
se enchufa al mismo `MMSimulation`. En ambos objetos, `sigma` representa `σ_H`; el simulador usa
incrementos `ΔS = σ_H/√H · Z` para que su varianza terminal sea `σ_H²`. Estrategia y simulación
deben recibir el mismo `sigma` y alinear `horizon == steps`. Demuestra herencia + especialización.

## Presentación (3 bloques)

1. **De dónde sale el modelo** — Maximizas utilidad CARA sobre tu riqueza final con inventario incierto. Usamos τ=(H−t)/H y σ_H como volatilidad de precio del horizonte completo; así σ_H²τ es la varianza restante.
2. **Reservation price y optimal spread** — r es el mid ajustado por inventario y varianza restante; d es cuánto separas las cotizaciones. Al cierre, el término de riesgo se apaga pero permanece el término de liquidez.
3. **Simular y barrer gamma** — MMSimulation mueve el mid con incrementos σ_H/√H y te ejecuta según la distancia. Más gamma controla mejor el inventario, pero captura menos spread. No hay free lunch.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `14_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L14. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
