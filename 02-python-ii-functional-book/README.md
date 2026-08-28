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
reciben `book` explícitamente — anticipan la API de `OrderBook` en L5: métricas sin
argumentos como properties (`book.best_bid`, `book.mid`) y operaciones parametrizadas
como métodos (`book.imbalance(levels)`). Cero clases: el objetivo es *sentir el dolor* del estado
compartido.

El deck a medida (Pyodide) trae un **libro vivo** interactivo: añades/cancelas órdenes y ves
best_bid/ask, spread, mid e imbalance reaccionar. El núcleo son 7 ejercicios que culminan en
"construye y lee tu libro"; el auxiliar cuenta cuántas funciones reciben `book` (7 → puente a
POO). `order_book.py` consolida las funciones + un `main` 1:1 con el núcleo.

## Ejercicios de construcción

- **1. Tu fábrica de órdenes** — funciones que devuelven datos
- **2. Añade al libro** — listas: append
- **3. Cancela una orden, paso a paso** — for + if + append
- **4. Comprime el filtro** — list comprehension
- **5. Mejor bid y mejor ask** — max / min con filtro
- **6. Imbalance del libro** — presión compra/venta
- **7. Spread y mid, componiendo funciones** — componer funciones
- **8. Construye y lee tu libro** — juntar todas las funciones
- **9. Lista nueva no significa deep copy** — identidad y referencias
- **10. Una función como criterio** — sorted(key=get_price)
- **11. Sustituye el nombre por lambda** — lambda como callback

## Estructura de la carpeta

- `presentation/` — documento interactivo (o deck) + guion del profesor
- `exercises/02_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/02_auxiliary.ipynb` — el gimnasio: drills + profundización opcional

## Idea central

> Funciones sueltas que comparten el mismo estado están pidiendo a gritos ser un objeto.
