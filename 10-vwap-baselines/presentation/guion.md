# Guion — Clase 10: VWAP I — Baselines de volumen

**Idea central:** No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP reparte donde hay volumen.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Por qué trocear

- **Qué decir:** Una orden grande de golpe barre el libro y paga slippage. Repartirla en el tiempo reduce el impacto. Esa es la idea de un algoritmo de ejecución.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: TWAP: trozos iguales

- **Qué decir:** El baseline más simple: parte el objetivo en N trozos iguales, uno por intervalo. Ignora el volumen, pero es honesto y difícil de batir sin información.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: VWAP: pondera por volumen

- **Qué decir:** El mercado no negocia igual todo el día. VWAP pone más cantidad donde hay más volumen, para acercarse al precio medio ponderado por volumen.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
