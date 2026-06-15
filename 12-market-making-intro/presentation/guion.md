# Guion — Clase 12: Market making — Intro

**Idea central:** El market maker gana el spread, pero su enemigo es el inventario: cotiza para volver a plano.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: De dónde sale el PnL

- **Qué decir:** Compras en el bid, vendes en el ask, te quedas el spread. Si el flujo es equilibrado, ganas en cada vuelta. El problema es cuando no lo es.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Riesgo de inventario y adverse selection

- **Qué decir:** Si solo te compran (te quedas corto) o solo te venden (te quedas largo), acumulas posición justo cuando el mercado va en tu contra. Eso es adverse selection.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Skew por inventario

- **Qué decir:** La defensa: cuando estás largo, baja tus dos cotizaciones para que te compren menos y te vendan más, y vuelvas a plano. El reservation price hace justo eso.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
