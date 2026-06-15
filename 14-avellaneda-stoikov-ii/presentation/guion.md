# Guion — Clase 14: Avellaneda-Stoikov II — Simulación

**Idea central:** Más gamma = más miedo al inventario: cotizas más defensivo, cargas menos posición, pero capturas menos spread.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Simular para entender

- **Qué decir:** MMSimulation mueve el mid con un paseo aleatorio y te ejecuta según la distancia de tus cotizaciones. Ves la senda de inventario y el PnL marcado a mercado.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: A-S controla el inventario

- **Qué decir:** Frente a un market maker naive, el A-S mantiene el inventario mucho más cerca de 0: el reservation price lo empuja a soltar antes de cargar demasiado.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: El barrido de gamma

- **Qué decir:** gamma es la perilla de aversión. Súbela y el inventario máximo baja, pero también las vueltas (menos PnL). Bájala y pasa lo contrario. No hay free lunch.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
