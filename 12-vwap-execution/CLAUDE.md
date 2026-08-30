# Clase 12 — VWAP — Ejecución (guía de implementación)

Pieza del framework: **VWAPStrategy: slicing, TWAP y perfil de volumen estático**.

## Teoría que cubre

Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.

## Implementación técnica

`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick calcula el objetivo acumulado del perfil y emite una market order por la brecha
frente a los fills simulados por el motor canónico. Solo `on_fill` aumenta el volumen ejecutado: enviar una orden no
equivale a llenarla. Sin perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al
`Backtest` exactamente igual que cualquier otra — primera demostración del valor del framework de L10.

La predicción dinámica de volumen queda como profundización **OPTIONAL**: ningún contenido ni
assessment posterior la presupone; LIVE + REQUIRED se sostienen con slicing, TWAP, el perfil
VWAP estático y una comparación empírica honesta.

## Presentación (3 bloques)

1. **Por qué trocear** — Una orden grande de golpe barre el libro y paga slippage. Repartirla en el tiempo reduce el impacto.
2. **TWAP vs VWAP** — TWAP parte en trozos iguales; VWAP pondera por el perfil de volumen para acercarse al precio medio ponderado por volumen.
3. **OPTIONAL · Volumen dinámico** — Profundización no evaluable: el perfil fijo asume que hoy es como la media. Puedes probar una predicción con los últimos k, pero el replay actual enseña que añadir un modelo no garantiza mejorar el baseline y ninguna lesson posterior lo presupone.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `12_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El snapshot de `exchange/` declara exactamente la superficie disponible en L12. La lección construye su pieza sobre esa superficie; el snapshot siguiente conserva el estado acumulado sin presuponer que cada clase añada un módulo nuevo.
