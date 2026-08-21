# Guion — Clase 7: Del snapshot real al OrderBook

**Idea central:** el CSV termina en la frontera del sistema; desde ahí, todo el motor habla con `OrderBook`.

**Apertura literal:** “No voy a volver a enseñaros qué es un order book. Voy a enseñaros cómo convertimos datos externos en el objeto que ya conocéis.”

## Núcleo presencial · ≈20 min

### 1. El problema · 2 min
- Enseña una fila real: `bid_price_1`, `bid_size_1`, `ask_price_1`, `ask_size_1`.
- Pregunta qué objetos y contenedores deberían existir al otro lado de la transformación.

### 2. Scrolly fila → objeto · 10 min
- Haz una pausa por transición: raw → `Level` → bids/asks → ordenación.
- Usa el panel acumulado: cada parada debe terminar señalando qué líneas nuevas existen y qué estado producen.
- Contrasta `Order` (intención individual) con `Level` (liquidez agregada a un precio).
- En `sorted(key=...)`, conecta con las lessons anteriores. No reexpliques `sorted`.
- El núcleo presencial puede terminar aquí. La factory y la API permanecen como recorrido autónomo requerido.
- Antes de `@classmethod`, compara constructor normal y constructor alternativo. Solo después nombra `cls`.
- Regla: el resto del sistema no debe conocer los nombres de las columnas.

### 3. Scrubber · 5 min
- Cede el slider a un alumno.
- Framing: “Acabáis de construir la transformación para una fila; ejecutadla mentalmente 500 veces”.
- Señala que cada posición produce otro `OrderBook` coherente mediante la misma factory.

### 4. Aplicación cuantitativa · 3 min
- Pide la predicción antes de contar.
- No conviertas imbalance/microprice en el centro de la sesión: son consumidores de la API construida.

## Práctica guiada · ≈20 min
- En clase: B1–B4.
- Si sobra tiempo: iniciar B5.
- Consolidación requerida: B5–B8, incluida la comparación contra la referencia real.

## Puente
- “Ya tenemos estado ordenado y consultable. Mañana programamos qué ocurre cuando una orden intenta cambiarlo.”
- En el recorrido autónomo, el alumno debe abrir “Ver la clase” y reconocer cada fragmento visto.
