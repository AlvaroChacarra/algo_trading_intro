# L8 — VWAP Volume Baselines

**Duración:** 40 min (20 min HTML + 15 min notebook + ejercicios)  
**Prerequisito:** L7 LOB Modeling Examples

## Misión

Cambiar de escala: de microsegundos (LOB snapshot) a horas (ejecución institucional). Pregunta central: cómo distribuir una orden grande a lo largo del día sin mover el mercado. La respuesta — construir un VWAP schedule basado en el perfil de volumen intradiario — requiere predecir la forma U y el efecto día de la semana.

## Ideas centrales

1. **Market impact es real** — comprar 10 BTC de golpe cuesta $41.80 más por BTC que fragmentar
2. **El volumen tiene forma** — U-shape (open/close pico, midday valle) + efecto DOW (viernes 1.33× lunes)
3. **El contexto mejora el baseline** — mean_monday bate a mean_all en −19% RMSE para los lunes

## Archivos

| Archivo | Rol |
|---------|-----|
| `presentation/vwap-volume-baselines-interactive.html` | Presentación HTML 20 min (GSAP + Chart.js + D3) |
| `presentation/guion.md` | Script del instructor |
| `lesson.ipynb` | Notebook 19 celdas — demo guiada |
| `exercises/vwap_volume_exercises.ipynb` | Exercise 0 + 10 ejercicios |
| `data/btc_volume_intraday.csv` | 6048 filas, 7 columnas |
| `data/mean_profile.csv` | Perfil medio exportado para L9 |
| `CLAUDE.md` | Referencia técnica para Claude Code |

## Flujo de la clase

```
HTML (20 min) → lesson.ipynb (15 min, celdas 1-16) → ejercicios individuales
```

## Estado al final de la clase

Los alumnos han construido:
- 4 baselines de volumen (mean/median, global/weekday)
- `build_vwap_schedule(total_qty, volume_profile)` — función central
- `rmse_profile(pred_profile, eval_df)` — función de evaluación
- `select_best_profile(dow, profiles)` — helper contextual

## Datos

| Fuente | Descripción |
|--------|-------------|
| `data/btc_volume_intraday.csv` | 21 días × 288 intervalos de 5 min, U-shape sintético + ruido |
| `data/mean_profile.csv` | Exportado por `lesson.ipynb` celda 19 para uso en L9 |

## Continuidad

**Desde L7:** bridge directo — "en L7 predecíamos el siguiente snapshot; hoy cambiamos a escala de horas"  
**Hacia L9:** `data/mean_profile.csv` se carga directamente en L9 como baseline de referencia; L9 añade rolling window dinámico
