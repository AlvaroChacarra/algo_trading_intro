# Clase 3 — Python III — Módulos y errores

> Sacar las funciones del libro del notebook y meterlas en un módulo .py reutilizable que puedes importar desde otro archivo. Y blindarlo: que un libro vacío no lo reviente.

## Contexto teórico

Cuando tus funciones crecen, no pueden vivir sueltas en un notebook: las guardas en un
archivo `.py` — un **módulo** — y lo **importas** desde donde lo necesites. `import order_book`
trae el módulo entero; `from order_book import spread` trae solo una función. Así reutilizas
código sin copiarlo, que es justo lo que harás con el paquete `exchange/` desde la clase 7
(`import exchange`).

La segunda mitad de la clase son los **errores**: una función como `best_bid` revienta con un
libro vacío. `try/except` atrapa el fallo y devuelve algo sensato; `raise` lanza un error claro
cuando el dato no tiene sentido. Una librería de verdad no se cae con un dato raro.

## Qué construyes hoy

**tu order_book.py se vuelve un módulo importable y robusto**

Pre-paquete: se trabaja con el módulo `order_book.py` (las funciones de L2) y un `main.py`
que lo importa. El deck a medida (Pyodide) escribe el módulo en el sistema de archivos virtual y
lo importa en vivo. Conceptos: `import` vs `from ... import`, alias, `try/except`, `raise`,
excepciones propias, `if __name__ == "__main__"` y argumentos por defecto. El núcleo (6) culmina
construyendo y leyendo un libro a través del módulo importado; el `.py` entregable es
`order_book.py` (módulo) + `main.py` (lo importa). Puente: el código ya es una librería, pero
datos y funciones siguen separados → juntarlos = objetos (L4).

## Ejercicios de construcción

- **1. Importa una función del módulo** — from ... import
- **2. Importa el módulo entero** — import módulo
- **3. Blinda con try/except** — manejo de errores
- **4. Lanza un error claro** — raise
- **5. Combina funciones del módulo** — usar varias del módulo
- **6. Construye y lee un libro con el módulo** — juntar el módulo

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/03_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/03_auxiliary.ipynb` — el gimnasio: drills + profundización opcional

## Idea central

> Tu código deja de vivir en celdas: se vuelve una librería que importas. Y una librería de verdad no se cae con un dato raro.
