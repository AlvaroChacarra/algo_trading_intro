# Guion — Clase 4: OOP I — Order y Fill

**Idea central:** el `dict` de orden se convierte en un **objeto** `Order` que sabe operar consigo mismo (`order.notional()`), y modelamos la ejecución con `Fill` y su `cash_flow` (con signo). Hilo: el objeto `Order`. Primer módulo del paquete `exchange`. Clímax/puente: Order→Fill→dinero; falta quién lleva la cuenta → composición (L5).

Presentación interactiva (Pyodide + inspectores en JS). ~18 min.

---

## Hero · El reto (2 min)
- **Callback a L3:** "`order_book.spread(book)` — dato y función separados. ¿Y si el dato supiera operar consigo mismo?"
- **Decir:** "Una orden que calcula su propio nocional: `order.notional()`. Eso es un objeto, y arranca el paquete `exchange`."

## Bloque 1 · De dict a clase (3 min)
- **Pantalla:** el morph dict→atributos; ejecuta el editor que define `Order` y accede a `order.side`.
- **Decir:** "`__init__(self, ...)` guarda los datos en `self`, el propio objeto. Las claves del dict son ahora atributos."

## Bloque 2 · Métodos — el Order inspector (4 min)
- **Pantalla:** el inspector: cambia side/price/size y ve `notional` y `repr` actualizarse.
- **Decir:** "`notional()` no recibe argumentos: ya tiene los datos dentro (`self`). El comportamiento viaja con el dato. Antes `compute_notional(order)`, ahora `order.notional()`."

## Bloque 3 · __repr__ (3 min)
- **Pantalla:** ejecuta el editor con `__repr__`; **borra el método y reejecuta** para ver el `<Order object at 0x...>`.
- **Decir:** "Con `__repr__` el objeto decide cómo se muestra."

## Bloque 4 · Fill y cash_flow (4 min)
- **Pantalla:** el visualizador de signo: alterna compra/venta y ve el `cash_flow` cambiar de signo y color.
- **Decir:** "Una orden ejecutada es un `Fill`. Su `cash_flow` es negativo si compras (sale caja), positivo si vendes. Ese signo es la base de todo el PnL."

## Bloque 5 · El puente (3 min)
- **Decir:** "Tienes Order→Fill→cash_flow, pero cada fill es un evento suelto. ¿Quién suma los cash_flows y lleva caja, posición y equity? Falta un objeto que CONTENGA. Eso es composición — la clase 5 (`OrderBook` y `PositionTracker`)."

## Mini test (3 min)
- 5 A/B/C: `__init__`, método vs función, `__repr__`, signo del cash_flow, `self`.

## Cierre (1 min)
- Recoge los 3 puntos y manda al notebook: construir `Order` y `Fill`, guardarlas en `orders_demo.py` (primer módulo del paquete `exchange`).

## Checklist
- [ ] dict → clase: `__init__`, `self`, atributos.
- [ ] método `notional()` (el dato opera consigo mismo).
- [ ] `__repr__` (el objeto se describe).
- [ ] `Fill.cash_flow()` con signo (compra −, venta +).
- [ ] Puente: falta quién contiene y lleva la cuenta → composición (L5).
- [ ] Mini test.
