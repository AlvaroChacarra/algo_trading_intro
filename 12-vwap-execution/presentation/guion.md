# Guion — Clase 12: VWAP — Ejecución

**Idea central:** No mandes la orden de golpe: repártela. TWAP reparte en el tiempo; VWAP, según un perfil de volumen. Un modelo solo merece quedarse si los datos demuestran que mejora el baseline.

**Formato:** documento interactivo (`vwap-execution-doc.html`), autocontenido y sin internet. Tú haces scroll y narras. Regla de la casa: **"lo cian se toca"**.

Estructura: hero/reto (2 min) → scrollytelling (~7 min, scroll lento: cada parada es una idea) → simulador estrella (cede el teclado) → secciones de construcción (con gates de predicción: exige la predicción antes del ▶) → quiz (diagnóstico) → mapa del paquete + puente.

## Los bloques conceptuales


### 1. Por qué trocear

- **Qué decir:** Una orden grande de golpe barre el libro y paga slippage. Repartirla en el tiempo reduce el impacto.

### 2. TWAP vs VWAP

- **Qué decir:** TWAP parte en trozos iguales; VWAP pondera por el perfil de volumen para acercarse al precio medio ponderado por volumen.

### 3. OPTIONAL · Volumen dinámico

- **Qué decir:** Profundización no evaluable: el perfil fijo asume que hoy es como la media. Puedes probar una predicción con los últimos k, pero el replay actual enseña que añadir un modelo no garantiza mejorar el baseline y ninguna lesson posterior lo presupone.

## Cierre
- Recoge la idea central sobre el mapa del paquete y manda al notebook de construcción; presenta el gimnasio (dosis mínima declarada).
