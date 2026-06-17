# Guion — Clase 9: El loop de simulación

**Idea central:** Mercado = estado (libro) + dinámica (matching) + tiempo (el loop). Todo junto, ya simulas.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: step() avanza el tiempo

- **Qué decir:** Market.step() reconstruye el libro desde el siguiente snapshot y lo devuelve. Cuando se acaban, devuelve None. Ese es tu reloj.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: submit() ejecuta contra el libro actual

- **Qué decir:** En cada paso puedes enviar una orden: m.submit(order) la cruza contra el libro de ese instante y te devuelve los fills.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: PositionTracker lleva la cuenta

- **Qué decir:** Aplicas cada fill al tracker y en cualquier momento consultas equity(mid). Esa es tu curva de PnL.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
