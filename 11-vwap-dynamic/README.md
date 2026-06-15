# Clase 11 — VWAP II — Volumen dinámico

> El perfil fijo asume que hoy es como la media. Pero el flujo reciente informa. Predecir el volumen del próximo intervalo a partir de los anteriores afina el schedule.

## Contexto teórico

El perfil fijo asume que hoy se parece a la media. Pero el **flujo reciente informa**: si
el volumen de los últimos intervalos se desvía, conviene reaccionar.
- **Ventana rolada**: predice el volumen del próximo intervalo como media de los últimos *k*.
- **Perfil dinámico**: normaliza las predicciones en pesos.
- **Factor de corrección**: si vas por detrás del plan, acelera; si vas por delante, frena.

Extensión opcional: predecir volumen con una **regresión** es el primer paso de ML aplicado;
la pendiente de mínimos cuadrados (cov/var) es lo que hace `LinearRegression` por dentro.

## Qué construyes hoy

**predecir el perfil de volumen con datos recientes**

Funciones de predicción en stdlib: `rolling_mean`, normalización a perfil, `correction(
target_so_far, executed, remaining)`. El perfil dinámico se pasa a `VWAPStrategy`. La
regresión a mano (`slope = cov/var`) mantiene el curso sin dependencias y desmitifica el ML.
Aquí encaja, como auxiliar, el antiguo pipeline de data science del curso.

## Ejercicios de construcción

- **1. Media rolada** — ventana de los últimos k
- **2. Predice el próximo volumen** — usar la ventana
- **3. Perfil dinámico** — normalizar predicciones
- **4. Factor de corrección** — ir a tiempo

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/11_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/11_auxiliary.ipynb` — profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> No basta con la media histórica: el volumen de los últimos minutos también te dice qué viene.
