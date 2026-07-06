# Clase 12 — VWAP — Ejecución (guía de implementación)

Pieza del framework: **VWAPStrategy: repartir una orden por el perfil de volumen (estático y dinámico)**.

## Teoría que cubre

Primer algoritmo de **ejecución**. Mandar una orden grande de golpe barre el libro y paga
impacto; **trocearla** en el tiempo lo reduce. Dos baselines:
- **TWAP** (time-weighted): trozos iguales en el tiempo. Honesto y difícil de batir sin info.
- **VWAP** (volume-weighted): pondera por el **perfil de volumen** intradía, para acercarse al
  precio medio ponderado por volumen — el benchmark estándar de ejecución institucional.

El perfil son pesos relativos: se normalizan, así que importan las proporciones, no la escala.

## Implementación técnica

`exchange/strategies/vwap.py` (`VWAPStrategy(symbol, side, total_size, horizon, profile)`):
en cada tick emite una market order del tamaño del trozo (peso normalizado × total). Sin
perfil → TWAP uniforme. Es una subclase de `Strategy`: se enchufa al `Backtest` exactamente
igual que cualquier otra — primera demostración del valor del framework de L8.

## Presentación (3 bloques)

1. **Por qué trocear** — Una orden grande de golpe barre el libro y paga slippage. Repartirla en el tiempo reduce el impacto.
2. **TWAP vs VWAP** — TWAP parte en trozos iguales; VWAP pondera por el perfil de volumen para acercarse al precio medio ponderado por volumen.
3. **Volumen dinámico** — El perfil fijo asume que hoy es como la media. Predecir el volumen del próximo intervalo con los últimos k afina el schedule.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `12_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
