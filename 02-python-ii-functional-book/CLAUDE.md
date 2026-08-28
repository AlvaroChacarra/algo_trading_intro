# Clase 2 — Python II — El libro funcional (guía de implementación)

Pieza del framework: **funciones add_order / cancel / imbalance**.

## Teoría que cubre

Una función encapsula una idea reutilizable. Un **libro de órdenes** es una lista de
órdenes; añadir, cancelar y medir presión son operaciones sobre esa lista. El **imbalance**
`(vol_buy - vol_sell)/(vol_buy + vol_sell)` resume de qué lado empuja el mercado en [-1, 1].

El momento clave es pedagógico: cuando cinco funciones distintas reciben todas el mismo
`book` como primer argumento y lo manosean, el código está pidiendo a gritos que `book` deje
de ser un dato pasivo y se convierta en un **objeto con métodos**. Ese es el puente a OOP.

## Implementación técnica

Funciones puras que construyen y transforman datos: `make_order`, `add_order(book, order)`,
`cancel_order(book, id)`, `best_bid/best_ask(book)`, `spread/mid(book)`, `imbalance(book)`. Todas
reciben `book` explícitamente — anticipan la API de `OrderBook` en L5: métricas sin
argumentos como properties (`book.best_bid`, `book.mid`) y operaciones parametrizadas
como métodos (`book.imbalance(levels)`). Cero clases: el objetivo es *sentir el dolor* del estado
compartido.

El deck a medida (Pyodide) trae un **libro vivo** interactivo: añades/cancelas órdenes y ves
best_bid/ask, spread, mid e imbalance reaccionar. El núcleo son 7 ejercicios que culminan en
"construye y lee tu libro"; el auxiliar cuenta cuántas funciones reciben `book` (7 → puente a
POO). `order_book.py` consolida las funciones + un `main` 1:1 con el núcleo.

## Presentación (3 bloques)

1. **Funciones que construyen datos** — Una función no solo calcula números: puede construir y devolver estructuras. `make_order(...)` te da un dict listo, sin repetir las llaves cada vez.
2. **Un libro es una lista de órdenes** — Añadir y cancelar son funciones que reciben el libro y lo devuelven cambiado. Recorrer niveles te da spread, mid e imbalance.
3. **El dolor que viene: estado compartido** — add_order, cancel, imbalance... todas reciben `book` como primer argumento y lo manosean. Eso es la señal de que `book` quiere ser un objeto con métodos. L3 lo vuelve módulo; L4 introduce objetos y L5 convierte el libro en uno.
4. **Bucles compactos: comprensión y expresión generadora** — Una comprensión con corchetes construye una lista nueva. Una expresión generadora sin corchetes produce un valor cada vez para que max, min o sum lo consuman sin crear esa lista. En ambos casos se lee: expresión, por cada elemento, si cumple el filtro.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `02_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

Aún sin paquete: el código se construye en celdas del notebook. El vocabulario de L1-L3 se convierte en los atributos de las clases en L4.
