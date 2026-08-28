# Guion — Clase 11: Primera estrategia + métricas

**Idea central:** Sin benchmark no hay estrategia: parent arrival juzga la decisión; cada decision mid juzga su ejecución.

**Formato:** documento interactivo (`first-strategy-metrics-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. Una estrategia con criterio

- **Qué decir:** Compra cuando el libro empuja arriba (imbalance positivo), vende cuando empuja abajo. Simple, pero ya es una decisión basada en microestructura.

### 2. Dos llegadas, dos preguntas

- **Qué decir:** El parent arrival es el primer mid y evalúa la decisión completa. Cada orden hija tiene su propio decision mid y mide solo su ejecución. No se mezclan.

### 3. Leer el resultado con honestidad

- **Qué decir:** final_equity, posición final, número de fills. Un equity positivo con inventario enorme no es una buena estrategia: es riesgo escondido.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
