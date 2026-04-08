# Lesson 07 — LOB Modeling Examples

## Propósito

Clase de 40 minutos que extiende el pipeline de L6 con features temporales (rolling window), exploración de overfitting (Decision Tree complexity curve), y reformulación de la predicción como fill probability. Central pedagógico: ver el overfitting con datos reales (DT train=100%, test=47.3%) y entender por qué Random Forest regulariza.

## Estructura de archivos

```
07-lob-modeling-examples/
├── README.md
├── CLAUDE.md
├── lesson.ipynb                    # 18 celdas — demo guiada
├── presentation/
│   ├── lob-modeling-interactive.html
│   └── guion.md
├── exercises/
│   └── lob_modeling_exercises.ipynb  # 10 ejercicios + Exercise 0
└── data/
    └── lob_modeling_features.csv   # Generado por lesson.ipynb celda 3
```

## Flujo de la clase

1. `lob-modeling-interactive.html` — 20 min (Hero + 3 bloques + Cierre)
2. `lesson.ipynb` — 15 min en clase (celdas 1-12, demo guiada)
3. `lob_modeling_exercises.ipynb` — ejercicios individuales

## Datos

| Fuente | Uso |
|--------|-----|
| `../../06-lob-data-science-pipeline/data/lob_features.csv` | Base de L6 (499 filas, 53 columnas) |
| `data/lob_modeling_features.csv` | + 3 features temporales + 2 targets fill (484 filas, 58 columnas) |

`lob_modeling_features.csv` se genera ejecutando el notebook. Es idempotente.

**Por qué 484 filas:** Las 3 features de rolling(5) generan NaN en las primeras 4 filas → `dropna()` → 499 − 15 = 484.

## Stack de la presentación

| Librería | Rol | CDN |
|----------|-----|-----|
| GSAP 3.12.5 | Scroll, nav, reveals, stagger, ScrollTrigger | cdnjs |
| Chart.js 4.4.2 | Complexity curve + rolling chart (B1, B2), doughnut gauge (B3) | jsdelivr |
| D3.js v7 | Árbol de decisión animado SVG (B2) | jsdelivr |

## Bloques de la presentación

| Bloque | Duración | Concepto principal | Interacción clave |
|--------|----------|--------------------|-------------------|
| Hero | 2 min | 49.3% → 2 palancas | Animación GSAP de entrada |
| B1: Memoria temporal | 6 min | Rolling features añaden señal | Slider N=1-10 actualiza Chart.js |
| B2: Overfitting | 6 min | Complexity curve DT | Slider max_depth, D3 árbol animado |
| B3: Fill probability | 5 min | Reformular como fill | Simulador LOB + slider imbalance→fill% |
| Cierre | 1 min | 3 takeaways + puente a L8 | Scroll |

## Decisiones de diseño clave

- **LR temporal supera RF (55.5% vs 52.7%):** Con 338 muestras de entrenamiento, la regularización L2 implícita de LR es mejor que la varianza de RF. No cambiar esto — es pedagógicamente valioso (más complejidad ≠ mejor).

- **Target fill_in_3 (no fill_in_10):** fill_in_10 tiene tasa de éxito ~75% (desbalanceado, RF apenas mejora baseline). fill_in_3 ≈ 50% — balanceado, RF logra +2.7pp. Siempre usar fill_in_3.

- **DT overfitting usa datos reales:** train=100%, test=47.3% emerge naturalmente de los datos. No modificar los datos para hacer el demo más dramático.

- **D3 árbol usa splits reales:** wmid ≤ 100200.5 (nodo raíz), imbalance_mean_5 ≤ 0.4255 (nivel 2 izquierda), mid_momentum_5 ≤ -2.0 (nivel 2 derecha). Estos valores vienen de sklearn con los datos reales.

- **Feature importance muy uniforme:** RF no identifica una feature claramente dominante. depth_ratio lidera con 15.85% pero los 7 features son similares. Esto es correcto con 484 muestras — no inflar importances.

## Constantes baked-in (validators y HTML)

| Constante | Valor |
|-----------|-------|
| `len(df)` | 484 (499 − 15 por rolling NaN) |
| `n_train` | 338 |
| `n_test` | 146 |
| `acc_lr_temporal` | 0.5548 (~55.5%) |
| `acc_dt_none_train` | 1.0000 (100%) |
| `acc_dt_none_test` | 0.4726 (~47.3%) |
| `acc_dt_depth2_train` | 0.5710 (~57.1%) |
| `acc_dt_depth2_test` | 0.5274 (~52.7%) |
| `acc_rf_test` | 0.5274 (~52.7%) |
| `best_feature` | `'depth_ratio'` (15.85% importance) |
| `fill_rate` | ~0.50 (fill_in_3) |
| `acc_rf_fill` | 0.5479 (~54.8%) |
| `fill_baseline` | ~0.52 (always predict majority class) |

## Continuidad

**Desde L6:** reutiliza `lob_features.csv`, retoma la LR del 49.3% como punto de partida.  
**Hacia L8:** los modelos de predicción de dirección/fill sirven como input para las decisiones de ejecución VWAP.
