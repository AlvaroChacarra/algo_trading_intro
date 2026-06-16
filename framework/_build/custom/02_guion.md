# Guion — Clase 2: El libro funcional

**Idea central:** organizamos el código con **funciones** y construimos un libro de órdenes (lista) que se puede añadir, cancelar y leer. Hilo único: el **`book`** y las funciones que lo manosean. Clímax: *todas reciben `book` → pide ser un objeto* (puente a L3).

Presentación interactiva (Pyodide + libro vivo en JS). ~18-20 min.

---

## Hero · El reto (2 min)
- **Decir:** "La clase pasada una orden era un `dict`. Pero un mercado es un LIBRO que cambia. Y si copias y pegas, añadir ETH te obliga a duplicarlo todo. Hoy lo resolvemos con funciones."
- **Callback a L1:** recuerda el dict de orden y el `mid`.
- **Salida:** "Quiero un libro que se construya, recorte y lea — sin reescribir código."

## Bloque 1 · ¿Qué es una función? (4 min)
- **Decir:** "Una función empaqueta una idea: entran parámetros, sale un resultado con `return`. Deja de repetir código."
- **Pantalla:** ejecuta `make_order` con BTC y con ETH (mismo código, otros argumentos → ahí está el ahorro). Usa el **predice** (¿qué devuelve? → un dict).
- **Salida:** "Una función-fábrica construye datos por mí."

## Bloque 2 · Un libro es una lista; añadir (3 min)
- **Decir:** "El libro es una `list`. `add_order(book, order)` hace `append` y lo devuelve. Fíjate: recibe `book`."
- **Pantalla:** ejecuta el editor; el libro crece.
- **Riesgo:** no entrar aún en mutar vs no mutar; se toca en el bloque 3.

## Bloque 3 · Cancelar = filtrar (3 min)
- **Decir:** "Cancelar es quedarte con lo que NO cancelas: un filtro con comprensión de lista."
- **Honestidad:** `add_order` muta, `cancel_order` devuelve uno nuevo. Mezclar las dos formas lía; en L3 el objeto lo gestiona por dentro.
- **Salida:** "Sé construir y recortar el libro."

## Bloque 4 · Leer el libro — LIBRO VIVO (5 min)
- **Pantalla:** el simulador del libro vivo. Añade compras/ventas, cancela (clic en una orden) y ve best_bid/best_ask/spread/mid e **imbalance** (barra verde/rojo) reaccionar.
- **Decir:** "best_bid = compra más alta; best_ask = venta más baja; imbalance = hacia dónde empuja el libro."
- **Aprovecha:** quita todas las ventas → imbalance +1; al revés → −1. Que lo vean mover.
- **Salida:** "Leer el libro son funciones que calculan sobre la lista."

## Bloque 5 · El patrón / clímax (4 min)
- **Decir:** "Mira tus 5 funciones: TODAS reciben `book`. El libro es un dato pasivo que arrastras a todas partes. ¿Y si el libro supiera hacerlo solo? `book.add(...)`, `book.imbalance()`. Eso es un OBJETO. Es la clase 3."
- **Pantalla:** las dos columnas de firmas (`func(book)` vs `book.metodo()`).
- **Salida (el puente):** "Un dato + las funciones que lo manosean = un objeto."

## Mini test (3 min)
- 5 preguntas A/B/C: `return`, utilidad de make_order, el patrón `book`, imbalance, best_bid. Feedback inmediato.

## Cierre (1 min)
- Recoge los 3 puntos y manda al notebook: construir el libro funcional con sus manos y guardarlo en un `.py` (que en L3 será una clase `OrderBook`).

## Checklist
- [ ] Función = entra/return; make_order escala a ETH cambiando argumentos.
- [ ] Libro = lista; add (append) y cancel (filtro).
- [ ] Leer: best_bid/ask, spread, imbalance (libro vivo).
- [ ] Clímax: todo recibe `book` → objeto (puente a L3).
- [ ] Mini test pasado.
