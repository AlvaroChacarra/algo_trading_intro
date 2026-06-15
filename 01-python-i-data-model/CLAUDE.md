# Clase 1 — Python I — El modelo de datos (guía de implementación)

Pieza del framework: **order y snapshot como dicts**.

## Teoría que cubre

Ejecutar código es solo esto: un programa (el intérprete de Python) lee texto, lo
entiende y produce una acción. No hay magia. Los errores no son castigos: son el
intérprete diciéndote dónde no puede continuar.

En trading, el dato más básico es un **snapshot** del mercado (mejor bid, mejor ask) y una
**orden** (lado, precio, tamaño). Con eso ya aparece el esqueleto de cualquier algoritmo:
**dato → cálculo → decisión**. Un snapshot da `spread = ask - bid` y `mid = (bid+ask)/2`; un
`if` sobre el spread ya es una decisión automática.

## Implementación técnica

Sin paquete todavía: se trabaja con tipos básicos (`int`, `float`, `str`), listas,
diccionarios, `for` e `if`, y funciones. Una orden es un `dict` con `symbol`, `side`, `price`,
`size`; un libro es una lista de esos dicts.

Continuidad: este vocabulario (`symbol/side/price/size`) será **literalmente** el de los
atributos de la clase `Order` en L3. Los dicts de hoy son los objetos de pasado mañana.

## Presentación (3 bloques)

1. **Tu código es texto que un programa ejecuta** — Un archivo .py no es magia: es texto. Python lo lee de arriba abajo y produce un resultado. Si algo falla, el error te dice exactamente dónde mirar — es información, no un castigo.
2. **Datos con nombre: variables, listas y diccionarios** — Una variable guarda un valor. Una lista agrupa varios. Un diccionario agrupa piezas con significado — justo lo que es una orden: side, price, size.
3. **Del dato a la decisión: for e if** — Un for repite trabajo sobre muchos datos; un if convierte una observación en una decisión. Con esas dos piezas ya puedes recorrer un libro de órdenes y reaccionar.

## Cuaderno de construcción

Patrón por ejercicio: enunciado → starter (`pass`/`None`) → validador (`assert` con mensaje claro, tolerancia `1e-9`) → solución guiada embebida.
Tiers: **Núcleo** = ej. 1-3 (en clase), **Si vamos bien** = resto, **Auxiliares** = cuaderno `01_auxiliary.ipynb`.

El contenido se genera desde `framework/_build/` — para editar esta clase, edita su spec y regenera con `build_course.py`. No edites a mano los notebooks.

## Continuidad

Aún sin paquete: las clases se construyen en celdas del notebook (estilo L1-L2). El vocabulario de hoy se convierte en los atributos de las clases en L3.
