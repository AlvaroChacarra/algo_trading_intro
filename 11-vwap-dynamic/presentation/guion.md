# Guion — Clase 11: VWAP II — Volumen dinámico

**Idea central:** No basta con la media histórica: el volumen de los últimos minutos también te dice qué viene.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: El límite del perfil fijo

- **Qué decir:** Un perfil medio ignora que hoy puede ser un día raro. Si el volumen real se desvía, tu schedule se queda corto o se pasa.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Predicción con ventana rolada

- **Qué decir:** Estima el volumen del próximo intervalo como la media de los últimos k. Barato, sin ML, y ya reacciona al régimen actual.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Factor de corrección

- **Qué decir:** Si vas por detrás del plan, acelera; si vas por delante, frena. Un factor que compara ejecutado vs objetivo mantiene el schedule a tiempo.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
