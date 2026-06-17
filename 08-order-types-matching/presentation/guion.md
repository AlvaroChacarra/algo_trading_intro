# Guion — Clase 8: Órdenes y matching

**Idea central:** La forma en que envías la orden decide tu coste: cruzar ya, o esperar barato y arriesgarte a no ejecutar.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: El motor de cruce

- **Qué decir:** MatchingEngine.process(order, book) recorre el lado contrario, consume liquidez y devuelve los fills. El libro queda modificado.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Market vs limit

- **Qué decir:** Una market cruza al precio que haga falta hasta llenarse (caro pero seguro). Una limit solo cruza a tu precio o mejor; el resto descansa (barato pero incierto).
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: IOC y FOK

- **Qué decir:** IOC cruza lo que pueda y cancela el resto (nada descansa). FOK es todo-o-nada: si no se llena entera, no se ejecuta nada.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
