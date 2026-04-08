# Lesson 08 — VWAP Volume Baselines

## Propósito

Clase de 40 minutos que introduce el problema de ejecución algorítmica (market impact, VWAP) y los baselines de predicción de volumen intradiario. Cambio de escala completo respecto a L6/L7: de snapshot (segundos) a intraday schedule (horas). Artefacto central: `build_vwap_schedule(total_qty, volume_profile)`.

## Estructura de archivos

```
08-vwap-volume-baselines/
├── README.md
├── CLAUDE.md
├── lesson.ipynb                    # 19 celdas — demo guiada
├── presentation/
│   ├── vwap-volume-baselines-interactive.html
│   └── guion.md
├── exercises/
│   └── vwap_volume_exercises.ipynb  # Exercise 0 + 10 ejercicios
└── data/
    ├── btc_volume_intraday.csv     # Dataset principal (6048 filas)
    └── mean_profile.csv            # Generado por lesson.ipynb celda 19 (para L9)
```

## Flujo de la clase

1. `vwap-volume-baselines-interactive.html` — 20 min (Hero + 3 bloques + Cierre)
2. `lesson.ipynb` — 15 min en clase (celdas 1-16, demo guiada)
3. `vwap_volume_exercises.ipynb` — ejercicios individuales

## Datos

| Fuente | Descripción |
|--------|-------------|
| `data/btc_volume_intraday.csv` | 21 días × 288 intervalos de 5 min = 6048 filas. Sintético seed=42. |
| `data/mean_profile.csv` | Perfil medio exportado para L9. Se regenera ejecutando lesson.ipynb. |

**Generación del dataset:**
```python
rng = np.random.default_rng(42)
N_DAYS = 21 (2025-12-01 a 2025-12-21, empieza en lunes)
INTERVALS_PER_DAY = 288 (cada 5 min)
BASE_DAILY_VOLUME = 25_000 BTC/día
u_shape = 1 + 1.2 * (cos(π × t))²  # normalizado a suma 1.0
DOW_MUL = {0:0.85, 1:0.95, 2:1.05, 3:1.10, 4:1.15, 5:1.10, 6:0.90}
Ruido diario: σ=0.08; Ruido intervalo: σ=0.15
```

## Stack de la presentación

| Librería | Rol | CDN |
|----------|-----|-----|
| GSAP 3.12.5 + ScrollTrigger | Reveals, hero, code reveal, takeaway timeline | cdnjs |
| Chart.js 4.4.2 | Perfil U (B2), schedule bars (B3) | jsdelivr |
| D3.js v7 | LOB sweep animado (Hero + B1), bars de market impact | jsdelivr |

## Bloques de la presentación

| Bloque | Duración | Concepto | Interacción clave |
|--------|----------|----------|-------------------|
| Hero | 2 min | 10 BTC sin mover el mercado | D3: botón "Compra todo ahora" → sweep LOB niveles |
| B1: Market Impact | 6 min | Slippage crece con el tamaño | Slider orden 0.5→14 BTC → D3 bars + slippage counter |
| B2: Perfil intradiario | 6 min | U-shape + efecto DOW | Toggle Mon/Fri Chart.js |
| B3: VWAP Schedule | 6 min | build_vwap_schedule + RMSE | Radio baselines + "Revelar RMSE" con GSAP |
| Cierre | 1 min | 3 takeaways + bridge L9 | Scroll |

## Constantes baked-in (validators y HTML)

| Constante | Valor | Uso |
|-----------|-------|-----|
| `n_rows` | 6048 | Ex1 validator |
| `n_days` | 21 | Ex1 validator |
| `mean_daily_vol` | 25152.2 | Ex2 validator (tolerancia ±200) |
| `monday_mean_daily_vol` | 21289.5 | Ex2 (soft: < mean_daily_vol) |
| `friday_mean_daily_vol` | 28325.0 | HTML stat panel |
| `mean_profile_sum` | 1.0 (exacto) | Ex3 validator |
| `open_close_ratio` | 2.2779 (≈ 2.28) | Ex3 validator (tolerancia 0.05) |
| `mean_profile_interval_0` | 0.00481216 | Ex4 (schedule[0] = 10 × this) |
| `mean_profile_interval_144` | 0.00211254 | HTML stat panel |
| `mean_monday_profile_interval_0` | 0.00406789 | Ex5 validator |
| `schedule_10btc_interval_0` | 0.04812157 | Ex4 validator (tolerancia 1e-4) |
| `rmse_mean_all` | 0.00052448 | Ex6 validator, HTML RMSE table |
| `rmse_median_all` | 0.00053042 | HTML RMSE table |
| `rmse_mean_monday_global` | 0.00059731 | HTML RMSE table |
| `rmse_mean_monday_monday` | 0.00042372 | Ex7 validator, HTML RMSE table |
| `best_baseline_global` | `'mean_all'` | Ex7 validator |
| `best_baseline_monday` | `'mean_monday'` | Ex7 validator |
| `concentration_ratio` | 2.28 | Ex10 validator (constante vs total_qty) |
| LOB slippage 1 BTC | $5.00/BTC | HTML Hero / B1 |
| LOB slippage 10 BTC | $41.80/BTC | HTML Hero / B1 |
| LOB total saving | $368 USD | HTML Hero / B1 |

## Decisiones de diseño clave

- **21 días exactos (no 15):** Para tener exactamente 3 muestras por día de la semana en el perfil weekday. Con solo 2 muestras, la media/mediana del lunes sería demasiado ruidosa para mostrar el DOW effect claramente.

- **U-shape con cos²:** Formula limpia que da ratio open/midday ≈ 2.28. Evitar funciones ad-hoc que son más difíciles de entender y reproducir.

- **`mean_monday` no bate `mean_all` globalmente:** `rmse_mean_monday_global=0.00059731` > `rmse_mean_all=0.00052448`. Solo gana en su dominio (lunes). Esta asimetría es el mensaje pedagógico central del B3.

- **LOB hardcodeado (10 niveles):** No cargado de CSV. Precios 100K-100.09K, tamaños 0.5-2.5 BTC sumando 14.4 BTC total. La animación D3 es determinista y no depende de datos externos.

- **`data/mean_profile.csv` para L9:** Continuity hook explícito. L9 carga este archivo directamente como baseline de referencia en lugar de regenerar los datos de L8.

## Continuidad

**Desde L7:** bridge en la primera celda — "en L7 predecíamos el siguiente snapshot; hoy cambiamos a horas"  
**Hacia L9:** `data/mean_profile.csv` exportado en la última celda; L9 añade rolling window de 5 min como señal dinámica
