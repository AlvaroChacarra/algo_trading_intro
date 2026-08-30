# Guion — Clase 9: Construir Market y su API

**Idea central:** `Market` añade tiempo y compone las piezas anteriores.

**Apertura literal:** “Ya construisteis el estado y la dinámica. Hoy los metemos dentro de un objeto que añade tiempo.”

## Núcleo presencial · ≈20 min

### 1. Anatomía del objeto · 5 min
- Lee primero el `__init__` literal y mapea cada asignación al inspector.
- Después mueve `_i` con el slider.
- Haz nombrar los seis atributos: snapshots, depth, engine, índice, timestamp y book actual.
- Estado inicial obligatorio: `_i == -1`, `_timestamp is None`, `book is None`.

### 2. Construir step() · 6 min
- Calcula `next_i = self._i + 1`: todavía no se ha mutado el cursor.
- Construye `next_book` con `OrderBook.from_snapshot` de L7 y valida `next_timestamp` con `_integer_timestamp(raw_timestamp)`, todo en variables locales.
- Solo después haz el commit conjunto: `_i = next_i`, `_timestamp = next_timestamp`, `book = next_book`.
- Haz fallar una fila: cursor, timestamp y book anteriores deben seguir intactos.
- Explica el final como estado explícito: `_timestamp=None`, `book=None`, `return None`.
- El panel acumulado debe terminar mostrando `step()` entero.

### 3. Construir submit() · 5 min
- Antes del primer step, pulsa conceptualmente submit: `RuntimeError`.
- Después, sigue la delegación a `self._engine.process(...)` de L8.
- Frase clave: “Market no vuelve a programar matching; contiene un engine y delega”.
- Contrasta explícitamente `Market IS-A MatchingEngine` (falso) con `Market HAS-A MatchingEngine` (composición).
- Deja `timestamp` para consolidación requerida, pero señala que procede del snapshot actual; no aparece por magia.

### 4. reset y loop · 4 min
- Reset restaura juntos `_i=-1`, `_timestamp=None` y `book=None`.
- Ahora sí enseña el while completo: cada llamada ya tiene una implementación imaginable.

## Práctica guiada · ≈20 min
- En clase: B1–B5.
- Consolidación requerida: B6–B8.
- En B8, exige que el alumno atribuya cada mutación al objeto responsable.

## Consolidación REQUIRED y evaluable
- `from_csv()` es la factory desde almacenamiento y `sample()` localiza el CSV sintético del curso.
- `snapshots` entrega una copia defensiva del replay; B7 ejercita directamente las tres APIs.
- No consumir tiempo central en I/O no las convierte en OPTIONAL: pueden aparecer en evaluación.

## Cierre
- “step cambia el estado; submit delega la dinámica; reset vuelve al origen.”
- En el recorrido autónomo, el alumno abre la clase completa y atribuye cada línea a Market, MatchingEngine u OrderBook.
