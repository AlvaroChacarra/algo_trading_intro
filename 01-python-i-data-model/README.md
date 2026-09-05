# Clase 1 — Python I — El modelo de datos

> Entender cómo CPython transforma nuestra intención en operaciones ejecutables y usar las primitivas de Python para leer un order book, calcular información y decidir.

## Contexto teórico

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

## Qué construyes hoy

**order y snapshot como dicts**

Sin paquete todavía: tipos básicos (`int`, `float`, `str`), listas, diccionarios, `for`,
`if` y funciones. Una orden es un `dict` con `symbol`, `side`, `price`, `size`; un libro es una
lista de esos dicts.

La presentación HTML (a medida, con **Pyodide** ejecutando Python real en el navegador) lleva 5
simuladores: texto→bits (`ord`/`bin`), CPython vs compilación nativa, el viaje de una línea con
**tokens/AST/bytecode reales** (`tokenize`/`ast`/`dis`), el editor en vivo, los retos de
romper-código y el rule builder. El notebook refuerza con `ord`/`bin` y `dis` (auxiliares A4-A5).

Continuidad: el vocabulario (`symbol/side/price/size`) reaparece en `OrderMini` en L4 y, tras
la migración explícita de firma, en el `Order` estable de `exchange`. Los dicts de L1 son el
estado que L4 convertirá en objetos.

## Ejercicios de construcción

- **1. Enciende el mercado** — variables
- **2. Spread y mid** — operaciones y tipos
- **3. Una lista de mids** — listas e indexing
- **4. Media con un bucle** — for y acumuladores
- **5. Una orden, y cómo leerla** — diccionarios: crear y acceder
- **6. Clasifica el mercado** — if / elif / else
- **7. Tu primer algoritmo** — dato → cálculo → decisión
- **8. Pregunta qué Python estás usando** — sys.implementation
- **9. Mira el bytecode real** — dis

## Estructura de la carpeta

- `presentation/` — presentación interactiva
- `exercises/01_build_exercises.ipynb` — construyes la pieza (rutas LIVE / REQUIRED / OPTIONAL declaradas)
- `exercises/01_auxiliary.ipynb` — el gimnasio: drills + profundización opcional

## Idea central

> Un algoritmo es siempre lo mismo: dato → cálculo → decisión.
