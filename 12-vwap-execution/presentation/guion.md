# Guion — Clase 12: VWAP — Ejecución

**Idea central:** No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP, donde hay volumen; y el flujo reciente afina el plan.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Por qué trocear

- **Qué decir:** Una orden grande de golpe barre el libro y paga slippage. Repartirla en el tiempo reduce el impacto.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: TWAP vs VWAP

- **Qué decir:** TWAP parte en trozos iguales; VWAP pondera por el perfil de volumen para acercarse al precio medio ponderado por volumen.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Volumen dinámico

- **Qué decir:** El perfil fijo asume que hoy es como la media. Predecir el volumen del próximo intervalo con los últimos k afina el schedule.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
