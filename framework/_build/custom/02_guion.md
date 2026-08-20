# Guion — Clase 2: El libro funcional

**Idea central:** del script duplicado a **una receta, N usos** (funciones) y a **un solo dato** (el `book`) con su equipo de funciones. El contador final —"7 funciones, todas reciben `book`"— es la semilla de toda la semana.

**Formato:** documento interactivo (`python-ii-functional-book-doc.html`), autocontenido, sin internet. "Lo cian se toca."

---

## §0 · Hero — el reto (3 min)
- **Decir:** "Anoche intentasteis añadir ETH. Esto pasó." Lee el script con las líneas duplicadas atenuadas: "copiar… pegar… rezar…".
- **Callback a L1:** es EXACTAMENTE la pregunta del puente de la clase pasada.
- **Salida:** "El conocimiento copiado es deuda; hay que escribirlo una vez."

## §1 · Scrollytelling — de copiar a recetas (7 min)
- **0/5 el dolor:** tres fórmulas iguales en rojo. "Tres de estas líneas son deuda."
- **1/5 def:** "una receta con huecos: se escribe una vez, se llama N veces. Si la fórmula cambia, un solo sitio."
- **2/5 make_order:** "la fábrica: nunca más un dict a mano con una clave mal escrita."
- **3/5 el book:** "TODAS las órdenes en UNA lista. Se acabó bid_btc, bid_eth…"
- **4/5 leerlo:** las métricas de L1 vuelven, ahora como funciones que reciben el book.
- **5/5 imbalance + el contador:** para en el "7 funciones · todas reciben book 🤔". **Di:** "guardad ese dato: es la pista de toda la semana". No lo resuelvas hoy.

## §2 · La fábrica (4 min)
- Ejecuta `make_order` + `add_order` (▶). Señala el patrón: cada función hace UNA cosa y su nombre no necesita comentario.
- **Tracer de `cancel_order`:** no leas primero la comprehension. Avanza orden por orden: condición falsa → no pasa; condición verdadera → entra en `new_book`. Al final, señala `book is new_book → False`.
- Cambia de «versión explícita» a «comprehension» solo después de entender el recorrido. La sintaxis nueva comprime un mecanismo ya visible: no borra, **construye una lista nueva**.

## §3 · El libro vivo (4 min)
- **Cede el teclado.** Cada botón registra abajo la llamada exacta (`add_order(book, make_order(…))`) — señálalo: "el botón sois vosotros llamando a vuestra función".
- Vacía el libro y mira las métricas en "—": lanza la pregunta trampa: "¿qué *debería* hacer best_bid con un libro vacío?" No la respondas — es el gancho de L3.

## §4 · Leer el libro (4 min)
- `best_bid` con max + generador: tradúcelo palabra a palabra.
- **El gate del imbalance:** que predigan (buy 0.3 + 0.3, sell 0.2). El resultado es `+0.50`: presión compradora. Repite el rango canónico: `−1` vendedor, `0` equilibrado, `+1` comprador.
- En el microtracer de `sorted(key=...)`, haz una ronda con `get_price`: función sin paréntesis = se entrega la función; `get_price(order)` = se obtiene un número. Después activa `lambda`: misma salida, función breve sin nombre.
- Honestidad (en el doc): los profesionales ponderan por cercanía al mid; se refina en L7.

## §5 · Quiz (3 min)
- 5 A/B/C. La pregunta 5 ("¿qué comparten las 7 funciones?") es el puente disfrazado — dale drama.

## §6 · Puente + mapa (2 min)
- Mapa: L1 ✓, L2 iluminada. "El sistema crece."
- **Puente:** "vuestras funciones mueren al cerrar el notebook. ¿Copiarlas a otro archivo? Ese es el pecado de esta mañana. La cura: vuestra propia librería importable. Próxima clase."
- Manda al notebook y al gimnasio (27 drills — con calentamiento de L1).

## Checklist
- [ ] Función = receta con huecos; un cambio, un sitio.
- [ ] El book único + make/add/cancel; la comprensión construye lista nueva.
- [ ] Estado = datos que describen cómo está ahora el sistema; todas las operaciones miran el mismo `book`.
- [ ] `sorted(key=get_price)` se entiende antes de sustituirlo por `lambda`.
- [ ] best_bid/best_ask/spread/mid como funciones de lectura.
- [ ] Imbalance canónico en `[-1,+1]`: signo y magnitud bien leídos.
- [ ] El contador "todas reciben book" queda plantado (sin resolver).
