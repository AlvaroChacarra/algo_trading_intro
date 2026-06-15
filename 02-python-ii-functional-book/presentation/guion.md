# Guion — Clase 2: Python II — El libro funcional

**Idea central:** Funciones sueltas que comparten el mismo estado están pidiendo a gritos ser un objeto.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Funciones que construyen datos

- **Qué decir:** Una función no solo calcula números: puede construir y devolver estructuras. `make_order(...)` te da un dict listo, sin repetir las llaves cada vez.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Un libro es una lista de órdenes

- **Qué decir:** Añadir y cancelar son funciones que reciben el libro y lo devuelven cambiado. Recorrer niveles te da spread, mid e imbalance.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: El dolor que viene: estado compartido

- **Qué decir:** add_order, cancel, imbalance... todas reciben `book` como primer argumento y lo manosean. Eso es la señal de que `book` quiere ser un objeto con métodos. Eso es la clase 3.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
