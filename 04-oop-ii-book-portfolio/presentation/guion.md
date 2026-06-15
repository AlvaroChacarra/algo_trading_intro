# Guion — Clase 4: OOP II — OrderBook y PositionTracker

**Idea central:** Composición: un OrderBook contiene niveles; un PositionTracker consume Fills. Los objetos se hablan entre sí.

Presentación de 3 bloques (~5-7 min cada uno) + hero + cierre.


## Bloque 1: Un objeto que contiene objetos

- **Qué decir:** El OrderBook guarda dos listas (bids y asks). Esas cinco funciones de la clase 2 que recibían book ahora son métodos: book.spread(), book.mid().
- **Acción en pantalla:** mostrar el snippet del bloque 1 y ejecutarlo en el notebook.

## Bloque 2: Estado privado y encapsulación

- **Qué decir:** El PositionTracker guarda _cash y _position con guión bajo: 'no me toques desde fuera, usa mis métodos'. apply_fill recibe un objeto Fill y actualiza el estado.
- **Acción en pantalla:** mostrar el snippet del bloque 2 y ejecutarlo en el notebook.

## Bloque 3: Los objetos colaboran

- **Qué decir:** tracker.apply_fill(fill): el tracker no sabe de precios sueltos, sabe de Fills. equity(mark) marca el inventario a mercado. Cada pieza tiene una responsabilidad.
- **Acción en pantalla:** mostrar el snippet del bloque 3 y ejecutarlo en el notebook.

## Cierre
- Recoge la idea central y manda abrir `exercises/`.
