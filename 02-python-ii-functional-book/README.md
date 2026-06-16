# Clase 2 — Python II — El libro funcional

> Pasar de scripts sueltos a funciones que construyen y modifican un libro de órdenes. Al final verás por qué tantas funciones compartiendo el mismo libro piden ser un objeto.

## Contexto teórico

Una función encapsula una idea reutilizable. Un **libro de órdenes** es una lista de
órdenes; añadir, cancelar y medir presión son operaciones sobre esa lista. El **imbalance**
`(vol_buy - vol_sell)/(vol_buy + vol_sell)` resume de qué lado empuja el mercado en [-1, 1].

El momento clave es pedagógico: cuando cinco funciones distintas reciben todas el mismo
`book` como primer argumento y lo manosean, el código está pidiendo a gritos que `book` deje
de ser un dato pasivo y se convierta en un **objeto con métodos**. Ese es el puente a OOP.

## Qué construyes hoy

**funciones add_order / cancel / imbalance**

Funciones puras que construyen y transforman datos: `make_order`, `add_order(book, order)`,
`cancel_order(book, id)`, `best_bid/best_ask(book)`, `spread/mid(book)`, `imbalance(book)`. Todas
reciben `book` explícitamente — anticipan exactamente los métodos de `OrderBook` en L4
(`book.best_bid()`, `book.imbalance()`). Cero clases: el objetivo es *sentir el dolor* del estado
compartido.

El deck a medida (Pyodide) trae un **libro vivo** interactivo: añades/cancelas órdenes y ves
best_bid/ask, spread, mid e imbalance reaccionar. El núcleo son 7 ejercicios que culminan en
"construye y lee tu libro"; el auxiliar cuenta cuántas funciones reciben `book` (7 → puente a
POO). `order_book.py` consolida las funciones + un `main` 1:1 con el núcleo.

## Ejercicios de construcción

- **1. Tu fábrica de órdenes** — funciones que devuelven datos
- **2. Añade al libro** — listas: append
- **3. Cancela una orden** — filtrar (comprensión de lista)
- **4. Mejor bid y mejor ask** — max / min con filtro
- **5. Imbalance del libro** — presión compra/venta
- **6. Spread y mid, componiendo funciones** — componer funciones
- **7. Construye y lee tu libro** — juntar todas las funciones

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/02_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/02_auxiliary.ipynb` — profundización opcional

## Idea central

> Funciones sueltas que comparten el mismo estado están pidiendo a gritos ser un objeto.
