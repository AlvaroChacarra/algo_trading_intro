# L7 — LOB Modeling Examples

**Duración:** 40 min (20 min HTML + 15 min notebook + ejercicios)  
**Prerequisito:** L6 LOB Data Science Pipeline

## Misión

Tomar el pipeline de L6 (que terminó en 49.3%) y mejorarlo en dos dimensiones: **memoria temporal** (features de rolling window) y **pregunta mejor** (fill probability en lugar de solo dirección). De paso, ver el overfitting en acción con datos reales.

## Ideas centrales

1. **Las features estáticas ignoran el pasado** — rolling mean/std/momentum añaden memoria y mejoran la señal
2. **Más complejidad ≠ mejor modelo** — el Decision Tree sin límite memoriza ruido (47.3% test vs 100% train)
3. **¿Se llena mi orden?** — reformular la predicción como fill probability da información más accionable que solo dirección

## Archivos

| Archivo | Rol |
|---------|-----|
| `presentation/lob-modeling-interactive.html` | Presentación HTML 20 min (GSAP + Chart.js + D3.js) |
| `presentation/guion.md` | Script del instructor |
| `lesson.ipynb` | Notebook 18 celdas — demo guiada |
| `exercises/lob_modeling_exercises.ipynb` | 10 ejercicios + Exercise 0 motivacional |
| `data/lob_modeling_features.csv` | 484 filas, 58 columnas |
| `CLAUDE.md` | Referencia técnica para Claude Code |

## Flujo de la clase

```
HTML (20 min) → lesson.ipynb (15 min, celdas 1-12) → ejercicios individuales
```

## Estado al final de la clase

Los alumnos han visto:
- 3 features temporales construidas con `.rolling(5)`
- Curva de complejidad DT con max_depth 1–10
- Random Forest con feature importance
- Fill probability como target alternativo (fill_in_3)

Los alumnos pueden replicar en los ejercicios:
- Añadir features temporales propias
- Reproducir la curva de complejidad
- Entrenar RF y leer feature importances
- Calcular fill probability por bucket de imbalance

## Datos

| Fuente | Uso |
|--------|-----|
| `../06-lob-data-science-pipeline/data/lob_features.csv` | Base (499 filas, 53 columnas) |
| `data/lob_modeling_features.csv` | + 3 features temporales + 2 targets fill (484 filas, 58 columnas) |

## Continuidad

**Desde L6:** reutiliza `lob_features.csv`, retoma la LR del 49.3%  
**Hacia L8:** los modelos de predicción aquí construidos se conectan a estrategias de ejecución VWAP
