# Clase 1 — Python I — El modelo de datos (guía de implementación)

Pieza del framework: **order y snapshot como dicts**.

## Teoría que cubre

**Un lenguaje de programación formaliza nuestra intención para que una máquina pueda
ejecutarla.** La línea `mid = (bid + ask) / 2` no llega directamente a la CPU. Python es el
lenguaje; **CPython** es su implementación estándar, escrita principalmente en C. CPython analiza
el source, lo compila a **Python bytecode** y ejecuta ese bytecode mediante su máquina virtual.

El viaje es: source → tokens → árbol (AST) → Python bytecode → CPython VM → CPU. El bytecode
contiene instrucciones para la VM y no es machine code nativo de x86-64 o ARM64. Por tanto:
**Python source ≠ bytecode ≠ machine code** y **CPython ≠ bytecode**.

C++ suele seguir otro pipeline: source → GCC/Clang/MSVC → machine code nativo → CPU. C++ ofrece
rendimiento, control y detección de muchos errores antes de ejecutar. Python destaca por su ciclo
`write → run → inspect → fix`, su interactividad y su ecosistema. Un **SyntaxError** impide compilar
el source; otros errores pueden aparecer cuando la VM alcanza la operación problemática. Sobre
este modelo construimos un algoritmo: **dato → cálculo → decisión** (snapshot → `spread`/`mid` →
un `if` que decide).

## Implementación técnica

Sin paquete todavía: tipos básicos (`int`, `float`, `str`), listas, diccionarios, `for`,
`if` y funciones. Una orden es un `dict` con `symbol`, `side`, `price`, `size`; un libro es una
lista de esos dicts.

El documento HTML autocontenido lleva 5 simuladores interactivos: texto→bits (`ord`/`bin`),
CPython vs compilación nativa, el viaje de una línea con **tokens/AST/bytecode reales**
(`tokenize`/`ast`/`dis`), el editor guiado, los retos de romper-código y el rule builder. Las
salidas de Python se calculan y validan durante la generación; el documento no ejecuta Python ni
carga una CDN en el navegador. El notebook refuerza con `ord`/`bin` y `dis` (auxiliares A4-A5).

Continuidad: el vocabulario (`symbol/side/price/size`) reaparece en `OrderMini` en L4 y, tras
la migración explícita de firma, en el `Order` estable de `exchange`. Los dicts de L1 son el
estado que L4 convertirá en objetos.

## Presentación (3 bloques)

1. **De intención humana a operaciones ejecutables** — Python es el lenguaje y CPython su implementación estándar: compila el source a bytecode y su VM lo ejecuta. El traceback permite un ciclo corto de escribir, ejecutar, observar y corregir.
2. **Datos con nombre: variables, listas y diccionarios** — Una variable guarda un valor. Una lista agrupa varios. Un diccionario agrupa piezas con significado — justo lo que es una orden: side, price, size.
3. **Del dato a la decisión: for e if** — Un for repite trabajo sobre muchos datos; un if convierte una observación en una decisión. Con esas dos piezas ya puedes recorrer un libro de órdenes y reaccionar.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Clasificación: **LIVE / REQUIRED / OPTIONAL**, decidida en `pedagogy/exercise_routes.yml`. Auxiliares: `01_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

Aún sin paquete: el código se construye en celdas del notebook. El vocabulario de L1-L3 se convierte en los atributos de las clases en L4.
