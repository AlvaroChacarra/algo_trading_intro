# L13 — Market Making: El oficio de proveer liquidez

## Misión
Entender qué hace un market maker, cómo gana dinero, y por qué el inventario es su principal
riesgo. La clase termina con la pregunta que L14 responde: ¿existe una manera matemáticamente
óptima de fijar bid y ask?

## Tres ideas clave

| Idea | Concepto |
|------|----------|
| El spread no es gratis | P&L = fills×s/2 − \|q\|×\|ΔS\|. El segundo término (inventario) puede superar al primero. |
| Inventario es el enemigo | Adverse selection, quote stale y volatilidad son la misma cosa: acumulas posición en el momento equivocado. |
| Las heurísticas son aproximaciones | Imbalance, L2, skew — funcionan pero no son óptimas. No garantizan el γ correcto ni el spread que maximiza E[utilidad]. |

## Flujo de clase

```
presentation/ (33 min)
  Hero:  LOB animado, MM cotiza, fills llegan en tiempo real
  B1:    Mecánica — 5 pasos animados + fórmula de P&L
  B2:    Tres riesgos — inventario / adverse selection / volatilidad
  B3:    Tres palancas — imbalance / nivel 2 / skew de inventario
         → preview de reservation_price = mid - q·γ·σ²

exercises/ (en clase y casa)
  E1–E3 (Núcleo):    price_path → NaiveMarketMaker → reservation_price
  E4–E5 (Núcleo):    SkewedMarketMaker → comparación naive vs skewed
  E6–E7 (Si vamos):  shock de volatilidad → grid search de gamma
  E8–E10 (Bonus):    descomposición P&L → imbalance MM → MarketMakingBacktest
```

## Parámetros de simulación

```python
SIGMA  = 0.05    # volatilidad del precio por step
SPREAD = 0.10    # spread total en precio
KAPPA  = 5.0     # decaimiento de fill prob: p = exp(-κ·δ)
ARR    = 1.0     # tasa de llegada base (órdenes/step)
```

## Resultado clave del notebook

`SkewedMarketMaker` reduce la varianza del inventario a **~55%** respecto al naive
(`std: 9.9 → 5.4`) y el inventario máximo de 26 a 15 lotes. El P&L mejora en términos
de riesgo ajustado aunque el valor absoluto varíe por simulación.

## Continuidad con L14
- `MarketMakingBacktest` (E10) acepta cualquier clase de MM, incluido el
  `ASMarketMaker` que se construye en L14.
- `reservation_price()` introducida aquí es el núcleo del resultado de Avellaneda-Stoikov.
  En L14 aparece con el factor `(T−t)` y con el spread óptimo derivado del modelo completo.
