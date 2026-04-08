# Lesson 09 — VWAP Dinámico + Cierre de Ciclo

## Propósito

Clase de 40 minutos que cierra el bloque de ejecución (L8-L9) y el ciclo completo (L4-L9). Extiende el schedule estático de L8 con un correction factor dinámico multiplicativo y culmina con `ExecutionDecision`, la clase que unifica las señales de L6/L7/L8/L9. No hay CSV propio — L9 reutiliza los datos de L8 y L7.

## Estructura de archivos

```
09-vwap-dynamic-models/
├── README.md
├── CLAUDE.md
├── lesson.ipynb                       # 16 celdas — dos actos
├── presentation/
│   ├── vwap-dynamic-interactive.html  # Mission Control theme
│   └── guion.md
└── exercises/
    └── vwap_dynamic_exercises.ipynb   # Exercise 0 + 10 ejercicios
```

Sin carpeta `data/` — L9 lee directamente de `../08-vwap-volume-baselines/data/` y `../07-lob-modeling-examples/data/`.

## Flujo de la clase

1. `vwap-dynamic-interactive.html` — 20 min (Hero + 3 bloques + Cierre)
2. `lesson.ipynb` — 15 min (celdas 1-15, demo guiada)
3. `vwap_dynamic_exercises.ipynb` — ejercicios individuales

## Datos usados

| Archivo externo | Descripción |
|----------------|-------------|
| `../08-vwap-volume-baselines/data/btc_volume_intraday.csv` | 21 días × 288 intervalos. TEST_DATE = '2025-12-21' (día 21). |
| `../07-lob-modeling-examples/data/lob_modeling_features.csv` | 484 snapshots LOB con imbalance_mean_5 y fill_in_3. |

## Constantes clave del notebook

| Variable | Valor | Origen |
|----------|-------|--------|
| `TOTAL_QTY` | 10.0 BTC | Tamaño de orden de ejemplo |
| `WINDOW` | 5 intervalos (25 min) | Frecuencia de reajuste CF |
| `TEST_DATE` | '2025-12-21' | Día 21 (último día del dataset) |
| `static_profile.iloc[0]` | 0.00476613 | Media de 20 días (train) — distinto al mean_profile de L8 que es 21 días |
| `cf_block_0` | 0.988095 | CF del primer bloque del día 21 |
| `max_dev_static` | 0.126737 BTC | Tracking deviation máxima, schedule estático |
| `max_dev_dynamic` | 0.027309 BTC | Tracking deviation máxima, schedule dinámico |
| `len(cf_hist)` | 57 | 288 / 5 = 57 bloques completos (el último no genera CF) |

## Constantes de ejercicios (validators)

| Ejercicio | Constante | Valor | Tolerancia |
|-----------|-----------|-------|-----------|
| E1 | `static_profile.iloc[0]` | 0.00476613 | 1e-5 |
| E2 | `cf_block_0` | 0.988095 | 1e-4 |
| E3 | `max_dev_static` | 0.126737 BTC | 0.01 |
| E4 | `max_dev_dynamic` | 0.027309 BTC | 0.01 |
| E4 | `len(cf_hist)` | 57 | exacto |
| E4 | invariante | `max_dev_dynamic < max_dev_static` | — |
| E6 | `days_dynamic_wins` | ≥ 13 de 16 | — |
| E6 | `mean_improvement_pct` | 35–60% | rango |
| E7 | LIMIT | `(0.62, 0.65, 1.35)` | exacto |
| E7 | MARKET | `(0.38, 0.35, 1.55)` | exacto |
| E7 | WAIT | `(0.50, 0.45, 0.65)` | exacto |
| E7 | LIMIT | `(0.60, 0.51, 0.90)` | exacto |
| E7 | WAIT (umbral) | `(0.55, 0.50, 1.0)` | exacto (umbrales estrictos >) |
| E8 | `len(decisions)` | 484 | exacto |

## Funciones clave

```python
def compute_correction_factor(realized_block: np.ndarray,
                               predicted_block: np.ndarray) -> float:
    pred_sum = predicted_block.sum()
    if pred_sum == 0:
        return 1.0
    return float(realized_block.sum() / pred_sum)

def walk_forward_dynamic(actual: np.ndarray, base_profile: np.ndarray,
                          window: int = 5) -> tuple:
    # Retorna (dynamic_schedule array[288], cf_history list[57])
    n = len(actual)
    schedule = base_profile.copy()
    dynamic_schedule = np.zeros(n)
    cf_history = []
    for j in range(0, n, window):
        dynamic_schedule[j:j+window] = schedule[j:j+window]
        if j + window < n:
            cf = compute_correction_factor(actual[j:j+window], schedule[j:j+window])
            cf_history.append(cf)
            schedule[j+window:] *= cf
    return dynamic_schedule, cf_history

class ExecutionDecision:
    IMBALANCE_BULL = 0.55   # imbalance > 0.55 = presión compradora
    FILL_MIN       = 0.50   # fill_prob > 0.50 = alta prob fill
    VOL_HIGH       = 1.20   # volume_ratio > 1.20 = día activo
    VOL_LOW        = 0.80   # volume_ratio < 0.80 = día tranquilo
    
    def decide(self) -> str:
        if self.imbalance > 0.55 and self.fill_prob > 0.50:
            return 'LIMIT'
        elif self.volume_ratio > 1.20 and (self.imbalance < 0.45 or self.fill_prob <= 0.50):
            return 'MARKET'
        else:
            return 'WAIT'
```

## Stack de la presentación

| Librería | Rol | CDN |
|----------|-----|-----|
| GSAP 3.12.5 + ScrollTrigger | Timeline cierre, reveal cards, semáforo | cdnjs |
| Chart.js 4.4.2 | Gráfico estático vs dinámico (B1), barras backtest (B2) | jsdelivr |
| D3.js v7 | Arcos de los gauges en B3 | jsdelivr |

## Bloques de la presentación

| Bloque | Duración | Concepto | Interacción clave |
|--------|----------|----------|-------------------|
| Hero | 2 min | Ejecución en tiempo real — terminal Mission Control | Botón "▶ Iniciar día" → setInterval 50ms |
| B1: CF | 6 min | `CF = realizado / predicho`, ajuste multiplicativo | Slider 0.3× → 3.0×, badge color cambia |
| B2: Backtest | 5 min | Walk-forward 16 días, estático vs dinámico | Animación racing bars, badge ganador por día |
| B3: ExecutionDecision | 6 min | 3 señales → LIMIT / MARKET / WAIT | 3 sliders independientes, semáforo GSAP |
| Cierre | 1 min | Timeline L4→L9 + bridge Exam-Quiz I | GSAP stagger 6 cards |

## Decisiones de diseño clave

- **TEST_DATE = día 21 (no leave-one-out):** Evaluación sobre el último día preserva la narrativa "hoy ejecutamos". El backtest de E6 usa los días 6-21 (16 días) para mostrar consistencia.

- **`static_profile.iloc[0] = 0.00476613` ≠ `mean_profile_interval_0 = 0.00481216` de L8:** En L9, el train es los primeros 20 días (excluye el día 21). En L8, el perfil medio es de los 21 días completos. Los validadores de E1 usan 0.00476613.

- **57 CF por bloque (no 58):** 288/5=57.6 → 57 bloques completos. El último bloque (intervalos 285-287, solo 3 intervalos) ejecuta pero no genera CF porque no hay schedule restante.

- **Tracking deviation como métrica de ejecución:** El CF dinámico no reduce el RMSE del perfil (los residuos son casi iid en datos sintéticos). Pero sí reduce dramáticamente el tracking deviation porque corrige el acumulado. Esta distinción es el mensaje pedagógico central de B1.

- **`volume_ratio = 1.0` para scan LOB en E8:** Los snapshots LOB de L7 son de una ventana temporal distinta al dataset de L8. No se pueden cruzar directamente. Se usa vol_ratio=1.0 como proxy "sin señal de volumen" para la demo.

## Continuidad

**Desde L8:** carga `btc_volume_intraday.csv` directamente. `mean_profile.csv` no se usa explícitamente (se regenera `static_profile` desde el CSV).  
**Hacia L10:** El Exam-Quiz I (L10) evalúa L4-L9. E10 es la tabla de repaso del bloque.
