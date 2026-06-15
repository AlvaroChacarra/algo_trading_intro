# Clase 1 — Python I — El modelo de datos

> De cero a entender que Python es texto que se ejecuta, y usarlo para guardar el primer dato de mercado: un snapshot y una orden.

## Contexto teórico

Ejecutar código es solo esto: un programa (el intérprete de Python) lee texto, lo
entiende y produce una acción. No hay magia. Los errores no son castigos: son el
intérprete diciéndote dónde no puede continuar.

En trading, el dato más básico es un **snapshot** del mercado (mejor bid, mejor ask) y una
**orden** (lado, precio, tamaño). Con eso ya aparece el esqueleto de cualquier algoritmo:
**dato → cálculo → decisión**. Un snapshot da `spread = ask - bid` y `mid = (bid+ask)/2`; un
`if` sobre el spread ya es una decisión automática.

## Qué construyes hoy

**order y snapshot como dicts**

Sin paquete todavía: se trabaja con tipos básicos (`int`, `float`, `str`), listas,
diccionarios, `for` e `if`, y funciones. Una orden es un `dict` con `symbol`, `side`, `price`,
`size`; un libro es una lista de esos dicts.

Continuidad: este vocabulario (`symbol/side/price/size`) será **literalmente** el de los
atributos de la clase `Order` en L3. Los dicts de hoy son los objetos de pasado mañana.

## Ejercicios de construcción

- **1. Enciende el mercado** — variables
- **2. Pon precio al snapshot** — aritmética
- **3. Crea tu primera orden** — diccionarios
- **4. Abre el libro** — listas de dicts
- **5. Mide la presión** — for e if

## Estructura de la carpeta

- `presentation/` — presentación interactiva + guion del profesor
- `exercises/01_build_exercises.ipynb` — construyes la pieza (núcleo 1-3, luego el resto)
- `exercises/01_auxiliary.ipynb` — profundización opcional

## Idea central

> Un algoritmo es siempre lo mismo: dato → cálculo → decisión.
