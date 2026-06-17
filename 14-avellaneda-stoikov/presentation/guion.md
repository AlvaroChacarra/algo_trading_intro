# Guion — Clase 14: Avellaneda-Stoikov — modelo y simulación

**Idea central:** El reservation price inclina según inventario y tiempo; el optimal spread cobra por el riesgo. Más gamma = más defensivo, menos inventario, menos PnL.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: De dónde sale el modelo

- **Qué decir:** Maximizas utilidad CARA sobre tu riqueza final con inventario incierto. La solución (vía HJB) da dos fórmulas cerradas.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Reservation price y optimal spread

- **Qué decir:** r es el mid ajustado por inventario y tiempo; d es cuánto separas las cotizaciones. Al cierre, el ajuste por inventario se apaga.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Simular y barrer gamma

- **Qué decir:** MMSimulation mueve el mid y te ejecuta según la distancia. Más gamma controla mejor el inventario, pero captura menos spread. No hay free lunch.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
