# Guion — Clase 10: El framework: Strategy + Backtest

**Idea central:** Escribe una subclase de Strategy y enchúfala al mismo Backtest. Eso es polimorfismo, y es lo que hace todo modular.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: La interfaz Strategy

- **Qué decir:** Una estrategia implementa on_book_update(book) y devuelve una lista de acciones (NewOrder/Cancel). No sabe nada del motor. Esa ignorancia es lo que la hace enchufable.
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Acciones, no efectos

- **Qué decir:** La estrategia no ejecuta órdenes: las pide. Devuelve NewOrder(order). El Backtest decide qué hacer con ellas. Separar decisión de ejecución es la clave del diseño.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: El Backtest lo cablea todo

- **Qué decir:** Recorre el mercado, pasa cada libro a la estrategia, ejecuta sus acciones contra el matching, actualiza el portfolio y mide. El mismo run() para cualquier estrategia.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
