# Lesson 06 — LOB Data Science Pipeline

## Propósito

Clase de 40 minutos que construye el pipeline conceptual y práctico para modelar variables del LOB. La pregunta central es "¿puedes predecir lo que pasará después?" La respuesta es sí — con condiciones. Esta es la clase del pipeline: menos foco en resultados, más en construirlo correctamente. Debe terminar con algo que corre.

## Estructura de archivos

```
06-lob-data-science-pipeline/
├── README.md
├── CLAUDE.md
├── lesson.ipynb                    # 20 celdas — pipeline completo
├── presentation/
│   ├── lob-ds-pipeline-interactive.html
│   └── guion.md
├── exercises/
│   └── lob_ds_pipeline_exercises.ipynb  # 10 ejercicios
└── data/
    └── lob_features.csv            # Generado por lesson.ipynb celda 2
```

## Flujo de la clase

1. `lob-ds-pipeline-interactive.html` — 20 min (Hero + 3 bloques + Cierre)
2. `lesson.ipynb` — 15 min en clase (demostración guiada)
3. `lob_ds_pipeline_exercises.ipynb` — ejercicios individuales

## Datos

| Fuente | Uso |
|--------|-----|
| `../../04-market-microstructure-btc/data/btc_lob_snapshots.csv` | Datos crudos (500 filas, 41 columnas) |
| `data/lob_features.csv` | Features derivados + target + leaky feature (499 filas tras drop NaN) |

`lob_features.csv` se genera ejecutando el notebook. Es idempotente (siempre produce el mismo resultado).

## Stack de la presentación

| Librería | Rol | CDN |
|----------|-----|-----|
| GSAP 3.12.5 | Scroll, nav, reveals, stagger, animación de leakage reveal | cdnjs |
| p5.js 1.9.4 | Diagrama animado de pipeline (B1), visualizador temporal train/test (B2) | cdnjs |
| Chart.js 4.4.2 | Scatter imbalance vs dirección (B3), bar chart baselines con slider (B3) | jsdelivr |

## Bloques de la presentación

| Bloque | Duración | Concepto principal | Interacción clave |
|--------|----------|--------------------|-------------------|
| Hero | 2 min | La pregunta: ¿puedes predecir? | — |
| B1: El pipeline | 6 min | 5 pasos del pipeline ML | Clic en nodos p5.js → panel de detalle |
| B2: Train/Test + Leakage | 6 min | Split temporal vs aleatorio + leakage | Toggle split mode + botón "Revela el leak" |
| B3: Baseline | 5 min | 3 baselines comparados | Slider de umbral de imbalance (Chart.js) |
| Cierre | 1 min | 5 takeaways + puente a L7 | Scroll |

## Decisiones de diseño clave

- **p5.js en clase conceptual (no solo simulación):** el diagrama de flujo con partículas y el visualizador temporal son animaciones espaciales/interactivas que justifican p5.js aunque L6 no sea una clase de simulación. El patrón `setInterval → redraw()` se usa para el pipeline (animación continua de partículas). El split visualizer usa `noLoop()` + `sk.redraw()`.

- **El feature leaky:** `realized_spread = ask_price_1[t+1] - bid_price_1[t]`. Se construye con `.shift(-1)`. La demostración de accuracy 49% → 88% es el momento central del bloque 2. No cambiar este feature.

- **Accuracy del LR = 49.3%:** Está por debajo del baseline always-UP (50.7%). Esto es pedagogicamente correcto y honesto. No ajustar los features para que LR "quede mejor". El resultado auténtico motiva L7.

- **best_feature = 'depth_ratio'** (0.5667 con umbral mediana), no imbalance. El validador del ejercicio 7 espera 'depth_ratio'. Si se regeneran los datos con otro seed, verificar que el resultado no cambia.

- **sklearn entra aquí por primera vez.** Solo `LogisticRegression`. No introducir árboles, random forests, ni cross-validation. Eso es L7.

## Constantes baked-in (validators y HTML)

| Constante | Valor |
|-----------|-------|
| `len(df)` | 499 (500 − 1 por dropna) |
| `spread_mean` | 11.396794 |
| `imbalance_std` | 0.097870 |
| `up_count` | 246 |
| `down_count` | 253 |
| `n_train` | 349 |
| `n_test` | 150 |
| `accuracy_always_up` | 0.506667 |
| `accuracy_threshold` (t=0.6) | 0.540000 |
| `lr_accuracy` | 0.493333 |
| `leaky_lr_accuracy` | 0.880000 |
| `best_feature` | 'depth_ratio' |

## Continuidad

**Desde L4:** reutiliza `btc_lob_snapshots.csv`; features mid, spread, imbalance son familiares.
**Desde L5:** el bridge de apertura referencia explícitamente la pregunta de fill probability de L5.
**Hacia L7:** el pipeline skeleton construido aquí se reutiliza verbatim. L7 añade más features, árboles, y comparación sistemática de modelos.
