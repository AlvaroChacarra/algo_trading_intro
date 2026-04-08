# Clase 6 — LOB Data Science Pipeline

## Misión

Construir el pipeline completo para modelar variables del libro de órdenes: desde datos crudos hasta un baseline funcionando, sin trampas.

## Ideas principales

- **Feature engineering:** mid, spread, imbalance, wmid, depth_ratio, spread_pct
- **Target definition:** dirección binaria (¿sube o baja el mid en t+1?)
- **Split temporal:** el test siempre en el futuro del train — nunca mezclar el tiempo
- **Data leakage:** un feature que usa `t+1` destruye la evaluación aunque parezca funcionar
- **Baseline:** el suelo mínimo antes de cualquier modelo complejo

## Ángulo de trading

Predecir la dirección del mid price de BTC con señales del LOB. El imbalance como señal de presión compradora. 54% de accuracy honesta (sin leakage) como punto de partida realista en un mercado eficiente.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `presentation/lob-ds-pipeline-interactive.html` | Presentación 20 min (GSAP + p5.js + Chart.js) |
| `presentation/guion.md` | Guión del instructor |
| `lesson.ipynb` | Notebook principal (20 celdas) |
| `exercises/lob_ds_pipeline_exercises.ipynb` | 10 ejercicios con validadores |
| `data/lob_features.csv` | Features derivados de btc_lob_snapshots.csv (generado por lesson.ipynb) |

## Estado al final de la clase

El alumno puede:
- Construir un pipeline de ML sobre datos de LOB sin leakage
- Explicar por qué el split temporal es obligatorio en series temporales
- Identificar un feature leaky y cuantificar su impacto
- Implementar y comparar tres baselines
- Leer una confusion matrix en términos de trading (FP = compraste y perdiste)
