# Guion — Clase 10: El framework: Strategy + Backtest

**Idea central:** Escribe una subclase de Strategy y enchúfala al mismo Backtest. Eso es polimorfismo, y es lo que hace todo modular.

**Formato:** documento interactivo (`strategy-framework-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. Recall L6 → contrato de producción

- **Qué decir:** En L6 todas las estrategias respondían a decide(imbalance) y devolvían una decisión. Conservamos el polimorfismo, pero el framework necesita más capacidad: recibe el libro completo y devuelve 0..N acciones; el motor ejecuta esas acciones.

### 2. La interfaz Strategy

- **Qué decir:** Una estrategia implementa on_book_update(book) y devuelve una lista de acciones (NewOrder/Cancel). No sabe nada del motor. Esa ignorancia es lo que la hace enchufable.

### 3. Acciones, no efectos

- **Qué decir:** La estrategia no ejecuta órdenes: las pide. Devuelve NewOrder(order). El Backtest decide qué hacer con ellas. Separar decisión de ejecución es la clave del diseño.

### 4. El Backtest lo cablea todo

- **Qué decir:** Recorre el mercado, pasa cada libro a la estrategia, ejecuta sus acciones contra el matching, actualiza el portfolio y mide. El mismo run() para cualquier estrategia.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
