# Guion — Clase 4: OOP I — Order y Fill

**Idea central:** el dict y sus funciones sueltas se funden en un **objeto**: nace `Order` (la intención) y `Fill` (el hecho consumado, con el **signo del dinero**). Primeras piezas del paquete `exchange/`.

**Formato:** documento interactivo (`oop-i-order-trade-doc.html`), autocontenido. "Lo cian se toca."

---

## §0 · Hero — el reto (2 min)
- **Decir:** "Tres clases llevamos con esta pareja: el dict con los datos y las funciones que lo reciben. Van siempre juntos pero viven separados — y vosotros hacéis de mensajeros. ¿Y si la orden supiera calcular su propio nocional?"
- **Salida:** "Datos + comportamiento en la misma pieza = clase."

## §1 · Scrollytelling — la metamorfosis (8 min)
- **0/5 separados:** "nadie es responsable de nada: un dict sin size no protesta."
- Etiqueta explícitamente las dos piezas antes de unirlas: dict = **estado**; funciones = **comportamiento**.
- **1/5 class + __init__:** "el molde y la fabricación. ¿Os suena? Es make_order de L2, ascendida."
- **2/5 self:** el momento delicado de la clase — dedícale tiempo. Dos tarjetas, datos independientes: "self es 'yo': el objeto concreto sobre el que trabaja el método".
- **3/5 métodos:** "compute_notional(order) se convierte en order.notional(): la cuenta vive donde viven los datos."
- **4/5 __repr__:** el antes/después (0x7f3a… vs Order(buy 0.5 @ 99950)): "cinco minutos que ahorran horas de debugging".
- **5/5 Fill y cash_flow:** el signo. "Comprar drena la caja; vender la llena."

## §2 · La clase completa (4 min)
- **El gate:** ¿qué imprime `order.notional()`? Pide predicción con tipo incluido (49975.0, float).
- La nota clave, en voz alta: "`order.notional()` es azúcar para `Order.notional(order)`. No hay magia, hay un convenio."

## §3 · El taller de órdenes (4 min)
- **Cede el teclado:** side/price/size en vivo → repr, notional, cash_flow.
- Insiste en la distinción de la nota: **notional** (tamaño de la apuesta, sin signo) vs **cash_flow** (lo que le pasa a tu caja, con signo). "Distinguirlos os salvará el PnL en L5."

## §4 · De la orden al dinero (3 min)
- Ejecuta el par de fills: compra a 99950, venta a 100050 → `+50.0`. "Vuestro primer PnL realizado, calculado por objetos."

## §5 · Quiz (3 min)
- 5 A/B/C: self, __init__, atributo vs método, __repr__, signo del cash_flow.

## §6 · Puente + mapa (2 min)
- Mapa: L1-L3 ✓, L4 iluminada — "primeras piezas DENTRO del paquete exchange/".
- **Puente:** "sabéis fabricar órdenes… y las tenéis sueltas por la memoria, como en L2 teníais variables sueltas. Falta el objeto que las contiene y el que lleva la cuenta cuando los fills empiezan a caer. Composición: próxima clase."
- Notebook + gimnasio (16 drills: el molde, Order/Fill, validación en __init__).

## Checklist
- [ ] class = molde; __init__ = fabricación; self = "yo".
- [ ] Objetos independientes del mismo molde.
- [ ] Método = la función mudada adentro; azúcar sintáctico entendido.
- [ ] La transformación visual termina en `estado + comportamiento → objeto`.
- [ ] __repr__ útil.
- [ ] cash_flow con signo: buy −, sell +.
