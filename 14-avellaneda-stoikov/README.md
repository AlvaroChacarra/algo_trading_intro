# L14 — Avellaneda-Stoikov: El Market Maker Óptimo

## Misión
Derivar y aplicar la solución analítica al problema de market making óptimo de
Avellaneda & Stoikov (2008). La clase responde la pregunta que L13 dejó abierta:
¿existe un γ correcto, un spread óptimo, una política que maximice utilidad esperada?

## Dos resultados clave

| Resultado | Fórmula |
|-----------|---------|
| Precio de reserva | `r(s,t) = s − q·γ·σ²·(T−t)` |
| Half-spread óptimo | `δ* = γ·σ²·(T−t)/2 + (1/γ)·ln(1 + γ/κ)` |

## Flujo de clase

```
presentation/ (35 min)
  Hero:  Dos fórmulas animadas — variables coloreadas con leyenda
  B1:    Tres ingredientes — BM (p5.js), Poisson (Chart.js), CARA (Chart.js)
  B2:    Ecuación HJB + pasos de derivación + interpretación de resultados
  B3:    Sliders interactivos (q, γ, σ, T−t, κ) → LOB en tiempo real
  B4:    Simulación Naive vs A-S, slider γ en tiempo real, shock σ×3

exercises/ (en clase y casa)
  E1–E2 (Núcleo):     as_reservation_price → as_optimal_halfspread
  E3–E5 (Núcleo):     ASMarketMaker → validación → comparación triple
  E6–E7 (Si vamos):   sensibilidad γ → shock de volatilidad
  E8–E10 (Bonus):     evolución δ*(τ) → calibración κ → informe completo
```

## Parámetros de simulación

```python
SIGMA  = 0.05    # volatilidad del precio por step
KAPPA  = 5.0     # decaimiento de fill prob: p = exp(-κ·δ)
ARR    = 1.0     # tasa de llegada base (órdenes/step)
T      = 3600    # duración de la sesión (steps)
```

## Resultado clave del notebook

`ASMarketMaker(γ=0.1)` sobre T=3600 (seed=42):
- **fills = 1414** (vs 774 naive en T=500, proporcional ~5643 para T=3600)
- **inv_std = 0.59** — inventario casi perfectamente controlado
- **max_abs_inv = 4** vs 26 del naive → **94% de reducción**

Tradeoff γ: γ=0.01 → 2475 fills / std=1.53 | γ=0.50 → 341 fills / std=0.27

## Continuidad con L13 y L15
- `reservation_price(mid, q, γ, σ²)` de L13 = `as_reservation_price` con τ=1 implícito.
- `MarketMakingBacktest` de L13 E10 acepta directamente `ASMarketMaker`.
- L15 (Exam-Quiz II) puede pedir diagnosticar o extender una implementación de MM.
