# Clase 1 — Python I — El modelo de datos (guía de implementación)

Pieza del framework: **order y snapshot como dicts**.

## Teoría que cubre

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

## Implementación técnica

Sin paquete todavía: tipos básicos (`int`, `float`, `str`), listas, diccionarios, `for`,
`if` y funciones. Una orden es un `dict` con `symbol`, `side`, `price`, `size`; un libro es una
lista de esos dicts.

La presentación HTML (a medida, con **Pyodide** ejecutando Python real en el navegador) lleva 5
simuladores: texto→bits (`ord`/`bin`), compilado vs interpretado, el viaje de una línea con
**tokens/AST/bytecode reales** (`tokenize`/`ast`/`dis`), el editor en vivo, los retos de
romper-código y el rule builder. El notebook refuerza con `ord`/`bin` y `dis` (auxiliares A4-A5).

Continuidad: el vocabulario (`symbol/side/price/size`) será **literalmente** el de los atributos
de la clase `Order` en L3. Los dicts de hoy son los objetos de pasado mañana.

## Presentación (3 bloques)

1. **Tu código es texto que un programa ejecuta** — Un archivo .py no es magia: es texto. Python lo lee de arriba abajo y produce un resultado. Si algo falla, el error te dice exactamente dónde mirar — es información, no un castigo.
2. **Datos con nombre: variables, listas y diccionarios** — Una variable guarda un valor. Una lista agrupa varios. Un diccionario agrupa piezas con significado — justo lo que es una orden: side, price, size.
3. **Del dato a la decisión: for e if** — Un for repite trabajo sobre muchos datos; un if convierte una observación en una decisión. Con esas dos piezas ya puedes recorrer un libro de órdenes y reaccionar.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = los primeros (en clase), **Si vamos bien** = el resto, **Auxiliares** = cuaderno `01_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

Aún sin paquete: el código se construye en celdas del notebook. El vocabulario de hoy se convierte en los atributos de las clases en L4.
