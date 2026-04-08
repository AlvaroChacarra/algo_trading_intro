# L9 — VWAP Dinámico + Cierre de Ciclo

**Duración:** 40 min (20 min HTML + 15 min notebook + ejercicios)  
**Prerequisito:** L8 VWAP Volume Baselines

## Misión

Cerrar el bloque de ejecución (L8-L9) y el ciclo completo (L4-L9). El schedule VWAP estático de L8 asume que el día de hoy seguirá el perfil histórico exacto. Cuando el mercado diverge, el executor se descuadra. Esta clase introduce el **correction factor dinámico** que reajusta el schedule cada 25 minutos, y culmina con `ExecutionDecision` — la clase que integra las señales de L6/L7/L8/L9 en una decisión ejecutable.

## Ideas centrales

1. **El correction factor adapta en tiempo real** — `CF = realizado / predicho` cada 25 min reduce el tracking deviation en ~78%
2. **La métrica de ejecución es tracking deviation, no RMSE** — lo que importa es cuántos BTC te descuadras del VWAP ideal
3. **Las señales se integran** — imbalance (L6/L7) + fill_prob (L7) + volume_ratio (L8/L9) → LIMIT / MARKET / WAIT

## Archivos

| Archivo | Rol |
|---------|-----|
| `presentation/vwap-dynamic-interactive.html` | Presentación HTML 20 min — Mission Control theme |
| `presentation/guion.md` | Script del instructor |
| `lesson.ipynb` | Notebook 16 celdas — dos actos (CF dinámico + ExecutionDecision) |
| `exercises/vwap_dynamic_exercises.ipynb` | Exercise 0 + 10 ejercicios |
| `CLAUDE.md` | Referencia técnica para Claude Code |

## Datos

No hay CSV propios. L9 carga directamente:
- `../08-vwap-volume-baselines/data/btc_volume_intraday.csv` — 21 días × 288 intervalos
- `../07-lob-modeling-examples/data/lob_modeling_features.csv` — 484 snapshots LOB

## Flujo de la clase

```
HTML (20 min) → lesson.ipynb (15 min) → ejercicios individuales
```

## Estado al final de la clase

Los alumnos han construido:
- `compute_correction_factor(realized_block, predicted_block)` — fórmula CF
- `walk_forward_dynamic(actual, base_profile, window=5)` — backtest sin look-ahead
- `ExecutionDecision` — árbitro que integra imbalance + fill_prob + volume_ratio
- Walk-forward backtest completo sobre 16 días (E6)

## Cierre de ciclo L4 → L9

| Clase | Pregunta central | Artefacto clave |
|-------|-----------------|----------------|
| L4 | ¿Cómo se estructura el LOB? | `btc_lob_snapshots.csv` + visualización bid/ask |
| L5 | ¿Cuándo se ejecuta una orden límite? | Fill probability empírica |
| L6 | ¿Puedes predecir la dirección del precio? | Pipeline ML + data leakage demo |
| L7 | ¿Qué modelo funciona mejor? | Overfitting demo + RandomForest + fill target |
| L8 | ¿Cuándo hay liquidez intradiaria? | `build_vwap_schedule(total_qty, profile)` |
| L9 | ¿Cómo adaptamos el schedule en tiempo real? | `walk_forward_dynamic()` + `ExecutionDecision` |

## Continuidad

**Desde L8:** `mean_profile.csv` exportado en L8 es la referencia. L9 usa el mismo dataset para extenderlo con CF dinámico.  
**Hacia L10:** Exam-Quiz I cubre todo L4–L9. L9 Exercise 10 es la tabla de repaso.
