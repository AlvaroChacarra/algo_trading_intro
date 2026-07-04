# Guion — Clase 8: Órdenes y matching

**Idea central:** La forma en que envías la orden decide tu coste: cruzar ya, o esperar barato y arriesgarte a no ejecutar.

**Formato:** documento interactivo (`order-types-matching-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. El motor de cruce

- **Qué decir:** MatchingEngine.process(order, book) recorre el lado contrario, consume liquidez y devuelve los fills. El libro queda modificado.

### 2. Market vs limit

- **Qué decir:** Una market cruza al precio que haga falta hasta llenarse (caro pero seguro). Una limit solo cruza a tu precio o mejor; el resto descansa (barato pero incierto).

### 3. IOC y FOK

- **Qué decir:** IOC cruza lo que pueda y cancela el resto (nada descansa). FOK es todo-o-nada: si no se llena entera, no se ejecuta nada.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
