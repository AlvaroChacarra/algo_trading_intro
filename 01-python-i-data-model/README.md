# Clase 1 — Python I — El modelo de datos

> De cero a entender que Python es texto que se ejecuta, y usarlo para guardar el primer dato de mercado: un snapshot y una orden.

## Contexto teórico

**Tu código es texto; una máquina solo entiende 1s y 0s. Python es el puente.** Un
procesador no lee "buy" ni "99950": solo maneja bits. Cada carácter es, por debajo, un número
(su código ASCII/Unicode) y ese número es una secuencia de bits.

Hay dos formas de salvar esa distancia: **compilar** (traducir todo el programa a binario de
una vez, como C) o **interpretar** (un programa lee y ejecuta sobre la marcha). Python es
**híbrido**: compila tu texto a un intermedio, el **bytecode**, y una **máquina virtual** (la
de CPython) interpreta ese bytecode. El viaje de una línea: texto → tokens → árbol (AST) →
bytecode → ejecución en la VM → instrucciones binarias en la CPU.

Esto explica hasta los errores: un **SyntaxError** es que Python no pudo ni *compilar* tu
texto; un **NameError/TypeError/ZeroDivisionError** es que compiló pero la VM *tropezó al
ejecutar*. Y sobre eso construimos la idea de algoritmo: **dato → cálculo → decisión**
(snapshot → `spread`/`mid` → un `if` que decide).

## Qué construyes hoy

**order y snapshot como dicts**

Sin paquete todavía: tipos básicos (`int`, `float`, `str`), listas, diccionarios, `for`,
`if` y funciones. Una orden es un `dict` con `symbol`, `side`, `price`, `size`; un libro es una
lista de esos dicts.

La presentación HTML (a medida, con **Pyodide** ejecutando Python real en el navegador) lleva 5
simuladores: texto→bits (`ord`/`bin`), compilado vs interpretado, el viaje de una línea con
**tokens/AST/bytecode reales** (`tokenize`/`ast`/`dis`), el editor en vivo, los retos de
romper-código y el rule builder. El notebook refuerza con `ord`/`bin` y `dis` (auxiliares A4-A5).

Continuidad: el vocabulario (`symbol/side/price/size`) será **literalmente** el de los atributos
de la clase `Order` en L3. Los dicts de hoy son los objetos de pasado mañana.

## Ejercicios de construcción

- **1. Enciende el mercado** — variables
- **2. Spread y mid** — operaciones y tipos
- **3. Una lista de mids** — listas e indexing
- **4. Media con un bucle** — for y acumuladores
- **5. Una orden, y cómo leerla** — diccionarios: crear y acceder
- **6. Clasifica el mercado** — if / elif / else
- **7. Tu primer algoritmo** — dato → cálculo → decisión

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/01_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/01_auxiliary.ipynb` — el gimnasio: drills + profundización opcional

## Idea central

> Un algoritmo es siempre lo mismo: dato → cálculo → decisión.
