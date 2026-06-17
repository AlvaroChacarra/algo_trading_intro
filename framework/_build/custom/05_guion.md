# Guion — Clase 5: OOP II — Composición y encapsulación

**Idea central:** construir los dos objetos del motor — `OrderBook` (que **contiene** niveles y se lee a sí mismo) y `PositionTracker` (que **lleva la cuenta**: caja, posición, equity). Hilo: esos dos objetos. Cierra el bloque OOP. Puente a L6: falta la herencia.

Presentación interactiva (Pyodide + inspector del libro + widget del tracker en JS). ~18 min.

---

## Hero · El reto (2 min)
- **Callback a L4:** "Tienes Order y Fill sueltos. ¿Quién los contiene y quién suma los cash_flows en caja/posición/equity?"
- **Decir:** "Hoy: `OrderBook` (composición) y `PositionTracker` (encapsulación). Los dos objetos del motor."

## Bloque 1 · Composición (4 min)
- **Pantalla:** el inspector — el libro **contiene** bids/asks, y a la derecha se lee a sí mismo con métodos (`book.best_bid()`, `book.mid()`, `book.imbalance()`). Pulsa "otro libro".
- **Decir:** "Las funciones de la clase 2 que recibían `book` ahora son métodos. No le pasas nada: usa lo que tiene dentro (`self.bids`). Eso es composición: un objeto que contiene objetos."

## Bloque 2 · Encapsulación (4 min)
- **Pantalla:** el widget del `PositionTracker`. Pulsa apply_fill(compra)/apply_fill(venta) y ve `_cash` y `_position`.
- **Decir:** "El guión bajo en `_cash`/`_position` dice: estado interno, tócalo con métodos (`apply_fill`), no a mano. `apply_fill` recibe un objeto `Fill`, no números sueltos."

## Bloque 3 · Equity (4 min)
- **Pantalla:** mueve el slider de `mark` y mira el equity cambiar (con la posición acumulada arriba). 
- **Decir:** "Tu valor total no es solo la caja: es `cash + position·mark`. Con posición distinta de cero, mover el precio mueve tu equity. Eso es marcar a mercado."

## Bloque 4 · El puente (3 min)
- **Decir:** "Ya tienes los dos objetos del motor. Sabes crear objetos (L4) y componerlos (L5). Falta la última pieza de OOP: cuando muchos objetos comparten un esqueleto y solo cambian un detalle — como las estrategias —, lo heredas. Herencia y polimorfismo: clase 6."

## Mini test (3 min)
- 5 A/B/C: composición, el guión bajo, `apply_fill` recibe Fill, equity, qué falta (herencia).

## Cierre (1 min)
- Recoge los 3 puntos y manda al notebook: construir `OrderBook` y `PositionTracker`, guardarlos en `book_demo.py`. Cierran OOP y son la base del motor (clase 7+).

## Checklist
- [ ] Composición: OrderBook contiene niveles; métricas como métodos.
- [ ] Encapsulación: `_cash`/`_position` privados, `apply_fill(fill)`.
- [ ] equity = cash + position·mark (marcar a mercado, slider).
- [ ] Puente: falta herencia/polimorfismo (L6).
- [ ] Mini test.
