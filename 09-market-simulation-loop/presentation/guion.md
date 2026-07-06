# Guion — Clase 9: El loop de simulación

**Idea central:** Mercado = estado (libro) + dinámica (matching) + tiempo (el loop). Todo junto, ya simulas.

**Formato:** documento interactivo (`market-simulation-loop-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. step() avanza el tiempo

- **Qué decir:** Market.step() reconstruye el libro desde el siguiente snapshot y lo devuelve. Cuando se acaban, devuelve None. Ese es tu reloj.

### 2. submit() ejecuta contra el libro actual

- **Qué decir:** En cada paso puedes enviar una orden: m.submit(order) la cruza contra el libro de ese instante y te devuelve los fills.

### 3. PositionTracker lleva la cuenta

- **Qué decir:** Aplicas cada fill al tracker y en cualquier momento consultas equity(mid). Esa es tu curva de PnL.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
