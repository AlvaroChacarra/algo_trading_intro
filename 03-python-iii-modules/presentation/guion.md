# Guion — Clase 3: Módulos y errores

**Idea central:** sacar las funciones del libro del notebook y meterlas en un **módulo** `order_book.py` que se **importa** y no se cae con datos raros. Hilo: el `order_book.py` de L2 → librería. Clímax/puente: datos y funciones aún separados → objetos (L4).

Presentación interactiva (Pyodide, con import en vivo desde el FS del navegador). ~18 min.

---

## Hero · El reto (2 min)
- **Decir:** "La clase pasada escribiste make_order, best_bid, imbalance… pero viven sueltas en celdas. ¿Cómo las reutilizas en otro archivo sin copiar? ¿Y cómo evitas que un libro vacío te reviente?"
- **Callback a L2:** las funciones que ya tienen.
- **Salida:** "Hoy mi código se vuelve una librería que importo."

## Bloque 1 · ¿Qué es un módulo? (3 min)
- **Decir:** "Un módulo es un archivo .py con funciones. Aquí está order_book.py. Pulsa Guardar: lo creo de verdad en el navegador."
- **Pantalla:** muestra el contenido del módulo; pulsa "Guardar order_book.py".
- **Salida:** "Un módulo es un archivo de funciones."

## Bloque 2 · Importar (4 min)
- **Decir:** "`import order_book` trae el módulo entero (usas `order_book.spread`); `from order_book import spread` trae solo eso."
- **Pantalla:** ejecuta el editor que importa y usa el módulo. **Si no guardaste el módulo → ModuleNotFoundError**: aprovéchalo: "un módulo tiene que existir para importarlo".
- **Riesgo:** Pyodide tarda al cargar la primera vez. El módulo se guarda solo al estar listo.
- **Salida:** "Importo y reutilizo sin copiar."

## Bloque 3 · __main__ (3 min)
- **Decir:** "Al importar, Python ejecuta el módulo. No quieres que imprima cosas solo por importarlo. El código de prueba va en `if __name__ == '__main__':`, que solo corre si ejecutas el archivo directamente."
- **Idea:** el módulo **define**; el script con `__main__` **hace**.
- **Salida:** "El módulo no se ejecuta al importarlo."

## Bloque 4 · Errores (4 min)
- **Decir:** "best_bid sobre un libro vacío revienta. `try/except` atrapa y da un plan B; `raise` lanza un error claro cuando el dato no tiene sentido."
- **Pantalla:** ejecuta `safe_best_bid([])` → None; con compra → el precio.
- **Salida:** "Una librería de verdad no se cae con un dato raro."

## Bloque 5 · El puente (3 min)
- **Decir:** "Tu código ya es una librería. Pero el `book` (datos) y las funciones van por separado: `order_book.spread(book)`. ¿Y si el libro supiera hacerlo solo? `book.spread()`. Juntar datos + funciones = un OBJETO. Eso es la clase 4."
- **Salida (puente):** "order_book.py se convertirá en la clase OrderBook."

## Mini test (3 min)
- 5 A/B/C: módulo, from-import, try/except, __main__, raise.

## Cierre (1 min)
- Recoge los 3 puntos y manda al notebook: importar el módulo, blindarlo y ejecutar main.py.

## Checklist
- [ ] Módulo = archivo .py con funciones; guardar e importar (en vivo).
- [ ] import vs from..import.
- [ ] __main__: el módulo no corre al importarlo.
- [ ] try/except (plan B) y raise (error claro).
- [ ] Puente: datos + funciones → objeto (L4).
- [ ] Mini test.
