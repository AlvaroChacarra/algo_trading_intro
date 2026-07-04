# Guion — Clase 5: OOP II — OrderBook y PositionTracker

**Idea central:** composición (objetos que **contienen** objetos) y encapsulación (estado **privado** con puerta única). Nacen las dos piezas serias del motor: el libro que se deja preguntar y el contable que nunca pierde la cuenta.

**Formato:** documento interactivo (`oop-ii-book-portfolio-doc.html`), autocontenido. "Lo cian se toca."

---

## §0 · Hero — el reto (2 min)
- **Decir:** "Ya fabricáis Orders y Fills… y están sueltos, como billetes fuera de la cartera. Dos preguntas que vuestro código no sabe responder: ¿cómo está el mercado? ¿cómo voy yo?"
- **Salida:** "Hoy: el libro y el contable."

## §1 · Scrollytelling — cajas dentro de cajas (7 min)
- **0/5 sueltas:** "cinco Orders en cinco variables. ¿Best bid? Nadie lo sabe: no hay libro."
- **1/5 OrderBook:** "composición: un objeto cuyos atributos son OTROS objetos. No hereda, no copia — TIENE bids y asks dentro."
- **2/5 métodos:** "las funciones de L2 se mudan adentro. Sin argumentos: el objeto ya tiene sus datos. Se acabó pasar book a todas partes" — cierra en voz alta el contador plantado en L2.
- **3/5 imbalance:** "la señal viaja con el libro. En L7 le daremos 500 snapshots reales."
- **4/5 _privado:** el guion bajo. "No bloquea nada: COMUNICA. Si cualquiera puede escribir tracker._cash = 999999, la contabilidad no vale nada."
- **5/5 equity:** la puerta única apply_fill y la fórmula: caja + posición × mark.

## §2 · El libro que se deja preguntar (4 min)
- **El gate:** ¿qué imprime `ob.mid()`? La gracia está en la composición doble: mid() llama a best_bid() y best_ask() — métodos que se apoyan en métodos.

## §3 · El contable en acción (5 min)
- **Cede el teclado:** fills de compra y venta + slider del mark. Reto: "acabad en verde".
- **El momento de oro** (está en la nota): compras al ask, vendes al bid → ida y vuelta sin que el precio se mueva = **pierdes el spread**. "Ese peaje invisible es la razón de ser del market maker — L13." Plántalo con solemnidad: es la semilla del bloque final del curso.

## §4 · Encapsulación (3 min)
- La honestidad del doc, en voz alta: `tracker._cash = 10**9` FUNCIONA. Python no es un banco suizo: es un contrato social. "Caja y posición deben moverse JUNTAS; la puerta única lo garantiza, tocar a mano lo rompe."

## §5 · Quiz (3 min)
- 5 A/B/C: composición, guion bajo, apply_fill, equity, por qué mid() sin argumentos.

## §6 · Puente + mapa (2 min)
- Mapa: L1-L4 ✓, L5 iluminada — "el motor ya tiene mercado y contabilidad".
- **Puente:** "falta quien DECIDE. Vais a escribir muchas estrategias que comparten esqueleto… ¿copiarlo cada vez? Ese pecado ya lo cometisteis en L2 y sabéis cómo huele. La cura se llama herencia."
- Notebook + gimnasio (15 drills: composición, privados, property y el gran reto libro+contable).

## Checklist
- [ ] Composición = objeto que contiene objetos.
- [ ] Métodos sin argumentos: el dato vive en self (cierre del contador de L2).
- [ ] _privado = convención, no candado; la puerta única apply_fill.
- [ ] equity = cash + position × mark.
- [ ] La ida y vuelta pierde el spread (semilla de L13) — plantada.
