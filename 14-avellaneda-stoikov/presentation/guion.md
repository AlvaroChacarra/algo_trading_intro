# Guion — Clase 14: Avellaneda-Stoikov — modelo y simulación

**Idea central:** El reservation price inclina según inventario y tiempo; el optimal spread cobra por el riesgo. Más gamma = más defensivo, menos inventario, menos PnL.

**Formato:** documento interactivo (`avellaneda-stoikov-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. De dónde sale el modelo

- **Qué decir:** Maximizas utilidad CARA sobre tu riqueza final con inventario incierto. La solución (vía HJB) da dos fórmulas cerradas.

### 2. Reservation price y optimal spread

- **Qué decir:** r es el mid ajustado por inventario y tiempo; d es cuánto separas las cotizaciones. Al cierre, el ajuste por inventario se apaga.

### 3. Simular y barrer gamma

- **Qué decir:** MMSimulation mueve el mid y te ejecuta según la distancia. Más gamma controla mejor el inventario, pero captura menos spread. No hay free lunch.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
