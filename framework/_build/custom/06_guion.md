# Guion — Clase 6: OOP III — Herencia y polimorfismo

**Idea central:** muchas estrategias comparten un esqueleto; en vez de copiarlo, se **hereda**. Construyes una familia `Strategy` de juguete (base + subclases) que en la clase 10 se convierte en el framework real. Hilo: la familia Strategy. Cierra el bloque OOP.

Presentación interactiva (Pyodide + simulador de polimorfismo en JS). ~18 min.

---

## Hero · El reto (2 min)
- **Callback a L5:** "Sabes crear objetos (L4) y componerlos (L5). Pronto tendrás muchas estrategias que comparten estructura."
- **Decir:** "¿Copias el esqueleto en cada una? No: lo heredas. Hoy construyes tu primera familia de estrategias — la semilla del framework de la clase 10."

## Bloque 1 · Herencia (4 min)
- **Pantalla:** el árbol Strategy → AlwaysBuy/AlwaysSell; ejecuta el editor (subclase hereda y sobrescribe; `isinstance`).
- **Decir:** "`class AlwaysBuy(Strategy)`: el paréntesis dice 'hereda de Strategy'. Solo escribes lo que cambia (`decide`)."

## Bloque 2 · El contrato (ABC) (4 min)
- **Pantalla:** ejecuta el editor con `ABC` + `@abstractmethod`. La última línea (`Strategy()`) lanza `TypeError`.
- **Decir:** "Una base abstracta obliga a las subclases a implementar `decide`. El contrato te protege de estrategias a medio hacer."

## Bloque 3 · Polimorfismo (4 min)
- **Pantalla:** el simulador — mueve el imbalance y mira a Momentum, Contrarian y Flat decidir cada uno lo suyo, con la **misma** llamada `s.decide(imbalance)`.
- **Decir:** "El bucle que las recorre no sabe cuál es cuál: llama `decide` y cada una responde a su manera. Eso es polimorfismo — y es lo que hace el motor intercambiable."

## Bloque 4 · El puente (3 min)
- **Decir:** "Esta familia de juguete es, en pequeño, el framework de la clase 10: una base `Strategy` con un método que cada estrategia implementa, enchufada al `Backtest`. Con esto cierras OOP: crear (L4), componer (L5), heredar (L6). En la clase 7 arranca el motor."

## Mini test (3 min)
- 5 A/B/C: herencia, `@abstractmethod`, polimorfismo, `super()`, el puente a L10.

## Cierre (1 min)
- Recoge los 3 puntos y manda al notebook: construir la familia `Strategy` (Momentum, Contrarian) y guardarla en `strategies_toy.py`.

## Checklist
- [ ] Herencia: subclase hereda y sobrescribe.
- [ ] ABC: `@abstractmethod` obliga a implementar (no se instancia incompleta).
- [ ] Polimorfismo: mismo método, objetos distintos (simulador).
- [ ] Puente: esta familia → framework real (L10).
- [ ] Mini test.
