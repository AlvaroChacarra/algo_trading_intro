# Guion — Clase 9: Construir Market y su API

**Idea central:** `Market` añade tiempo y compone las piezas anteriores.

**Apertura literal:** “Ya construisteis el estado y la dinámica. Hoy los metemos dentro de un objeto que añade tiempo.”

## Núcleo presencial · ≈20 min

### 1. Anatomía del objeto · 5 min
- Mueve `_i` con el slider.
- Haz nombrar los cinco atributos: snapshots, depth, engine, índice y book actual.
- Estado inicial obligatorio: `_i == -1`, `book is None`.

### 2. Construir step() · 6 min
- Ejecuta `self._i += 1` y muestra solo el cambio de cursor.
- Después llama visualmente a `OrderBook.from_snapshot` de L7.
- Explica el final como estado explícito: `book=None`, `return None`.

### 3. Construir submit() · 5 min
- Antes del primer step, pulsa conceptualmente submit: `RuntimeError`.
- Después, sigue la delegación a `self._engine.process(...)` de L8.
- Frase clave: “Market no vuelve a programar matching; contiene un engine y delega”.

### 4. reset y loop · 4 min
- Reset solo restaura `_i=-1` y `book=None`.
- Ahora sí enseña el while completo: cada llamada ya tiene una implementación imaginable.

## Práctica guiada · ≈20 min
- En clase: B1–B5.
- Consolidación requerida: B6–B8.
- En B8, exige que el alumno atribuya cada mutación al objeto responsable.

## Profundidad secundaria
- `from_csv()` es una factory desde almacenamiento.
- `sample()` es una comodidad del curso.
- No consumir tiempo central en I/O.

## Cierre
- “step cambia el estado; submit delega la dinámica; reset vuelve al origen.”
