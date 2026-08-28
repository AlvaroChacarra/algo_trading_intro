# Guion — Clase 13: Market making — Intro

**Idea central:** El market maker gana el spread, pero su enemigo es el inventario: cotiza para volver a plano.

**Formato:** documento interactivo (`market-making-intro-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. De dónde sale el PnL

- **Qué decir:** Compras en el bid, vendes en el ask, te quedas el spread. Si el flujo es equilibrado, ganas en cada vuelta.

### 2. Riesgo de inventario y adverse selection

- **Qué decir:** Si solo te compran o solo te venden, acumulas posición justo cuando el mercado va en tu contra. Eso es adverse selection.

### 3. Skew por inventario

- **Qué decir:** Cuando estás largo, baja tus dos cotizaciones para que te compren menos y te vendan más, y vuelvas a plano.

### 4. Puente LIVE a L14: gamma y kappa

- **Qué decir:** CARA da significado a gamma como aversión al riesgo. La intensidad lambda(delta)=A*exp(-kappa*delta) explica por qué alejar una quote reduce sus fills y qué controla kappa. L13 fija estas dos intuiciones sin exponer la clase ni las fórmulas de L14.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
