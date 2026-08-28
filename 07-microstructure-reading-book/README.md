# Clase 7 — Del snapshot real al OrderBook

> Convertir una fila real del feed en Level y OrderBook, y ampliar su API con depth, imbalance y microprice sin duplicar lógica.

## Contexto teórico

El problema de diseño es convertir una representación externa y plana en estado interno
con invariantes. Cada pareja precio/tamaño se agrupa en `Level`; los niveles se separan por lado;
el constructor ordena bids descendentes y asks ascendentes.

Una vez construida esa frontera, las métricas de microestructura son métodos del objeto:
`depth` agrega tamaños, `imbalance` compone dos llamadas a `depth` y `microprice` usa el primer
nivel. El conocimiento funcional de las métricas es previo; aquí importa programar la API.

## Qué construyes hoy

**OrderBook: transformar datos externos en estado ordenado y consultable**

`exchange/book.py`: `Level`, `OrderBook.__init__`, la factory
`OrderBook.from_snapshot`, `depth(side, levels)`, `imbalance(levels)` y `microprice`.

El notebook construye una versión del alumno desde un snapshot pequeño y termina aplicándola a
la primera fila real del CSV. Solo al final compara comportamiento con el `OrderBook` canónico;
no usa `Market` como caja negra.

## Ejercicios de construcción

- **B1 · Construye Level** — dataclass e independencia de objetos
- **B2 · Ordena bids y asks** — sorted(key=...)
- **B3 · Raw snapshot → niveles** — nombres dinámicos y bucle
- **B4 · Implementa from_snapshot** — @classmethod como factory
- **B5 · Implementa depth** — método de consulta
- **B6 · Implementa imbalance componiendo métodos** — reutilizar depth
- **B7 · Implementa microprice** — propiedad derivada del nivel 1
- **B8 · Snapshot real contra la referencia** — integración y oráculo

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/07_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/07_auxiliary.ipynb` — el gimnasio: drills + profundización opcional
- `exercises/exchange/` — el paquete que vienes construyendo (starter de hoy)

## Idea central

> El CSV termina en la frontera del sistema: desde ahí, todo el motor habla con OrderBook.
