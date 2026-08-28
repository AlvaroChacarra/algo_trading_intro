# Clase 3 — Python III — Módulos y errores (guía de implementación)

Pieza del framework: **tu order_book.py se vuelve un módulo importable y robusto**.

## Teoría que cubre

Cuando tus funciones crecen, no pueden vivir sueltas en un notebook: las guardas en un
archivo `.py` — un **módulo** — y lo **importas** desde donde lo necesites. `import order_book`
trae el módulo entero; `from order_book import spread` trae solo una función. Así reutilizas
código sin copiarlo, que es justo lo que harás con el paquete `exchange/` desde L4
(`import exchange`).

La segunda mitad de la clase son los **errores**: una función como `best_bid` revienta con un
libro vacío. `try/except` atrapa el fallo y devuelve algo sensato; `raise` lanza un error claro
cuando el dato no tiene sentido. Una librería de verdad no se cae con un dato raro.

## Implementación técnica

Pre-paquete: se trabaja con el módulo `order_book.py` (las funciones de L2) y un `main.py`
que lo importa. El deck a medida (Pyodide) escribe el módulo en el sistema de archivos virtual y
lo importa en vivo. Conceptos: `import` vs `from ... import`, alias, `try/except`, `raise`,
excepciones propias, `if __name__ == "__main__"` y argumentos por defecto. El núcleo (6) culmina
construyendo y leyendo un libro a través del módulo importado; el `.py` entregable es
`order_book.py` (módulo) + `main.py` (lo importa). Puente: el código ya es una librería, pero
datos y funciones siguen separados → juntarlos = objetos (L4).

## Presentación (3 bloques)

1. **Un módulo es un .py con funciones** — Cuando tus funciones crecen, las guardas en un archivo .py: eso es un módulo. Desde otro sitio lo importas y usas sus funciones, sin copiar nada.
2. **import vs from ... import** — `import order_book` trae el módulo entero (usas `order_book.fn`). `from order_book import spread` trae solo lo que pides (usas `spread`).
3. **Errores como red de seguridad** — best_bid sobre un libro vacío revienta. `try/except` lo atrapa; `raise` lanza un error claro cuando el dato no tiene sentido.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `03_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

Aún sin paquete: el código se construye en celdas del notebook. El vocabulario de L1-L3 se convierte en los atributos de las clases en L4.
