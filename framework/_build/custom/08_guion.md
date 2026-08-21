# Guion — Clase 8: Construir MatchingEngine

**Idea central:** planificar → validar → mutar.

**Apertura literal:** “Hoy no vais a usar un matching engine. Vais a programarlo.”

## Núcleo presencial · ≈20 min

### 1. Contrato · 2 min
- `Order + OrderBook → Fill[] + OrderBook modificado`.
- Pregunta: “¿Qué lado consume una BUY?” antes de iluminar asks.

### 2. Execution trace de process() · 10 min
- Una transición causal por parada: opposite → remaining → take → bug FOK → planned.
- El panel izquierdo acumula literalmente `process()`; no expliques una variable sin situarla dentro de esa función.
- En `take`, pide el cálculo mental antes de revelar `min(remaining, level.size)`.
- Antes de PLAN, ejecuta la versión ingenua: devuelve `[]`, pero el book ya cambió.
- Solo entonces introduce `planned` como solución al problema observado.

### 3. Tipos como políticas · 5 min
- Cambia MARKET/LIMIT/IOC/FOK sobre el mismo core.
- LIMIT: muestra `_crosses` simétrica BUY/SELL y `add_limit` del remanente.
- IOC: “misma planificación, misma ejecución; única diferencia: no descansa”.
- Evita cuatro definiciones funcionales largas: el objetivo es reutilización.
- El recorrido autónomo abre `_crosses`, el mapa de ramas y el código completo.

### 4. FOK · 3 min
- Ejecuta mentalmente la versión defectuosa que muta antes de saber si completa.
- Pregunta cómo garantizar todo o nada.
- Revela PLAN → VALIDATE → COMMIT.
- Regla final: “Cuando una operación puede abortarse, primero planifica y valida; después muta el estado.”

## Práctica guiada · ≈20 min
- En clase: B1–B3 y comienzo de B4.
- Consolidación requerida: B5–B10.
- B7 es DISEÑA; B8 es DEPURA + DISEÑA; no regalar el algoritmo antes de las pistas.
- En B10, comparar comportamiento y estado final, no el texto de la implementación.

## Puente
- “Sabéis cruzar una orden en una foto. Falta un objeto que elija qué foto es la actual y delegue en este engine.”
- Antes de cerrar, muestra que la función completa es la suma de las líneas construidas, no una nueva solución.
