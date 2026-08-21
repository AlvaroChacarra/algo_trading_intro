# Clase 7 — Del snapshot real al OrderBook (guía de implementación)

Pieza del framework: **OrderBook: transformar datos externos en estado ordenado y consultable**.

## Teoría que cubre

El problema de diseño es convertir una representación externa y plana en estado interno
con invariantes. Cada pareja precio/tamaño se agrupa en `Level`; los niveles se separan por lado;
el constructor ordena bids descendentes y asks ascendentes.

Una vez construida esa frontera, las métricas de microestructura son métodos del objeto:
`depth` agrega tamaños, `imbalance` compone dos llamadas a `depth` y `microprice` usa el primer
nivel. El conocimiento funcional de las métricas es previo; aquí importa programar la API.

## Implementación técnica

`exchange/book.py`: `Level`, `OrderBook.__init__`, la factory
`OrderBook.from_snapshot`, `depth(side, levels)`, `imbalance(levels)` y `microprice`.

El notebook construye una versión del alumno desde un snapshot pequeño y termina aplicándola a
la primera fila real del CSV. Solo al final compara comportamiento con el `OrderBook` canónico;
no usa `Market` como caja negra.

## Presentación (3 bloques)

1. **De fila a objetos** — Cada pareja price/size se convierte en un Level. Los bids y asks se separan y OrderBook impone el orden una sola vez.
2. **Una factory desde otra representación** — from_snapshot recorre la fila y fabrica la instancia. El resto del sistema deja de conocer nombres como bid_price_1.
3. **API por composición** — depth agrega tamaños; imbalance reutiliza depth; microprice reutiliza el mejor nivel. Cada método tiene una responsabilidad pequeña.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `07_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

El paquete `exchange/` llega con lo construido hasta la clase anterior; hoy se añade la pieza nueva, que se convierte en el starter de la siguiente.
