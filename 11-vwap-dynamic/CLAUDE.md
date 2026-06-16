# Clase 11 — VWAP II — Volumen dinámico (guía de implementación)

Pieza del framework: **predecir el perfil de volumen con datos recientes**.

## Teoría que cubre

El perfil fijo asume que hoy se parece a la media. Pero el **flujo reciente informa**: si
el volumen de los últimos intervalos se desvía, conviene reaccionar.
- **Ventana rolada**: predice el volumen del próximo intervalo como media de los últimos *k*.
- **Perfil dinámico**: normaliza las predicciones en pesos.
- **Factor de corrección**: si vas por detrás del plan, acelera; si vas por delante, frena.

Extensión opcional: predecir volumen con una **regresión** es el primer paso de ML aplicado;
la pendiente de mínimos cuadrados (cov/var) es lo que hace `LinearRegression` por dentro.

## Implementación técnica

Funciones de predicción en stdlib: `rolling_mean`, normalización a perfil, `correction(
target_so_far, executed, remaining)`. El perfil dinámico se pasa a `VWAPStrategy`. La
regresión a mano (`slope = cov/var`) mantiene el curso sin dependencias y desmitifica el ML.
Aquí encaja, como auxiliar, el antiguo pipeline de data science del curso.

## Presentación (3 bloques)

1. **El límite del perfil fijo** — Un perfil medio ignora que hoy puede ser un día raro. Si el volumen real se desvía, tu schedule se queda corto o se pasa.
2. **Predicción con ventana rolada** — Estima el volumen del próximo intervalo como la media de los últimos k. Barato, sin ML, y ya reacciona al régimen actual.
3. **Factor de corrección** — Si vas por detrás del plan, acelera; si vas por delante, frena. Un factor que compara ejecutado vs objetivo mantiene el schedule a tiempo.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `11_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
