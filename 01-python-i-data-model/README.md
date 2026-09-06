# Clase 1 — Python I — El modelo de datos

> Entender cómo CPython transforma nuestra intención en operaciones ejecutables y usar las primitivas de Python para leer un order book, calcular información y decidir.

## Tu recorrido de estudio

**Pregunta de hoy:** ¿Cómo paso de dos precios en pantalla a una decisión que otra persona pueda reproducir?

**Punto de partida.** Sin programar: con bid 99 y ask 101, distingue el coste de cruzar ambos lados del punto medio de la quote.

**Comprueba antes de avanzar:** Spread 2 y mid 100; ninguno dice por sí solo que comprar vaya a ser rentable.

Sigue los bloques en orden. En clase haces los **LIVE**; después completas los **REQUIRED** del principal, incluida la construcción en tus archivos. El auxiliar contiene solo variantes OPTIONAL. Los IDs históricos A/B identifican ejercicios, no su ruta. Los tiempos son orientativos, no un límite para aprender.

### 1. Nombrar y calcular una quote

Pon nombres al dato y unidades a cada cálculo; los ejercicios numéricos auxiliares consolidan después lo construido en clase.

**Presentación:** [escena 1](presentation/python-i-data-model-doc.html?mode=estudio#s0) · [escena 2](presentation/python-i-data-model-doc.html?mode=estudio#s1) · [escena 3](presentation/python-i-data-model-doc.html?mode=estudio#s2).

**Prepara y construye en el principal:** [B01](exercises/01_build_exercises.ipynb#L01-B01) (LIVE, 3 min) · [B02](exercises/01_build_exercises.ipynb#L01-B02) (LIVE, 4 min) · [A01](exercises/01_build_exercises.ipynb#L01-A01) (REQUIRED, 2 min) · [A02](exercises/01_build_exercises.ipynb#L01-A02) (REQUIRED, 2 min) · [A03](exercises/01_build_exercises.ipynb#L01-A03) (REQUIRED, 2 min).

**Puedes seguir cuando:** Explica por qué ask − bid es spread y por qué formatear o redondear no valida una orden.

### 2. Leer una secuencia sin perder observaciones

Pasa de índices a ventana y acumulador; conserva una predicción pequeña antes de ejecutar el bucle.

**Presentación:** [escena 4](presentation/python-i-data-model-doc.html?mode=estudio#s3).

**Prepara y construye en el principal:** [B03](exercises/01_build_exercises.ipynb#L01-B03) (LIVE, 3 min) · [B04](exercises/01_build_exercises.ipynb#L01-B04) (REQUIRED, 6 min) · [A13](exercises/01_build_exercises.ipynb#L01-A13) (REQUIRED, 2 min) · [A14](exercises/01_build_exercises.ipynb#L01-A14) (REQUIRED, 2 min).

**Puedes seguir cuando:** Identifica qué ticks entran y comprueba suma, longitud y media por separado.

### 3. Dar significado a los campos de una orden

Distingue texto recibido, número convertido y registro de orden; recupera el símbolo al mostrar el ticket.

**Presentación:** [escena 5](presentation/python-i-data-model-doc.html?mode=estudio#s4).

**Prepara y construye en el principal:** [B05](exercises/01_build_exercises.ipynb#L01-B05) (REQUIRED, 6 min) · [A06](exercises/01_build_exercises.ipynb#L01-A06) (REQUIRED, 2 min) · [A07](exercises/01_build_exercises.ipynb#L01-A07) (REQUIRED, 2 min) · [A08](exercises/01_build_exercises.ipynb#L01-A08) (REQUIRED, 2 min) · [A09](exercises/01_build_exercises.ipynb#L01-A09) (REQUIRED, 2 min) · [A18](exercises/01_build_exercises.ipynb#L01-A18) (REQUIRED, 2 min).

**Puedes seguir cuando:** Lee side, price y size sin mezclar claves y valores; explica cuándo un default es válido y cuándo ocultaría un campo obligatorio.

### 4. Cerrar dato → cálculo → decisión

La práctica LIVE termina clasificando el mercado y tomando una decisión; en el estudio autónomo comprueba además la puerta de permiso.

**Presentación:** [escena 6](presentation/python-i-data-model-doc.html?mode=estudio#s5) · [escena 7](presentation/python-i-data-model-doc.html?mode=estudio#s6) · [escena 8](presentation/python-i-data-model-doc.html?mode=estudio#s7).

**Prepara y construye en el principal:** [B06](exercises/01_build_exercises.ipynb#L01-B06) (LIVE, 4 min) · [B07](exercises/01_build_exercises.ipynb#L01-B07) (LIVE, 6 min) · [A11](exercises/01_build_exercises.ipynb#L01-A11) (REQUIRED, 2 min).

**Puedes seguir cuando:** Predice las ramas en los límites y separa señal buy, condiciones para operar y promesa de beneficio.

### Elige tu refuerzo OPTIONAL

Después de la ruta obligatoria, elige el bloque que responda a tu dificultad o curiosidad. No necesitas hacerlos todos; ninguno desbloquea una entrega ni añade materia evaluable. Regresa al ejercicio indicado y comprueba si ahora puedes explicarlo sin copiar.

| Si necesitas… | Practica | Aplica y vuelve |
|---|---|---|
| Si mezclas acumulación porcentual, suma y media. | [A4. Interés compuesto](exercises/01_auxiliary.ipynb#L01-A04) (2 min) · [A5. Agregados de un vistazo](exercises/01_auxiliary.ipynb#L01-A05) (2 min) | Compara potencias con incrementos simples y contrasta un bucle con agregados. Vuelve a [B04](exercises/01_build_exercises.ipynb#L01-B04). |
| Si una condición falla en el borde o confundes and con or. | [A10. Dentro de banda](exercises/01_auxiliary.ipynb#L01-A10) (2 min) · [A12. Señal y cautela](exercises/01_auxiliary.ipynb#L01-A12) (2 min) · [A25. Semáforo de presión](exercises/01_auxiliary.ipynb#L01-A25) (2 min) · [A26. Tarifa por tramos](exercises/01_auxiliary.ipynb#L01-A26) (2 min) | Cambia intervalos y magnitudes, pero conserva una tabla mental de casos y fronteras. Vuelve a [B06](exercises/01_build_exercises.ipynb#L01-B06). |
| Si confundes leer una lista, buscar un valor y modificarla. | [A15. Deshaz el último](exercises/01_auxiliary.ipynb#L01-A15) (2 min) · [A16. ¿Está el nivel?](exercises/01_auxiliary.ipynb#L01-A16) (2 min) · [A17. Ordena el lado bid](exercises/01_auxiliary.ipynb#L01-A17) (2 min) | Comprueba qué colección cambia y cuál conserva su orden original. Vuelve a [B03](exercises/01_build_exercises.ipynb#L01-B03). |
| Si cuesta distinguir presencia de una clave, valor guardado y actualización. | [A19. Actualiza la posición](exercises/01_auxiliary.ipynb#L01-A19) (2 min) · [A20. ¿Tiene el campo?](exercises/01_auxiliary.ipynb#L01-A20) (2 min) · [A21. Radiografía de comisiones](exercises/01_auxiliary.ipynb#L01-A21) (2 min) | Usa posiciones y comisiones para afianzar el registro sin mezclar unidades. Vuelve a [B05](exercises/01_build_exercises.ipynb#L01-B05). |
| Si un recorrido necesita varios intentos o el acumulador conserva el dato equivocado. | [A22. Ticks alcistas](exercises/01_auxiliary.ipynb#L01-A22) (2 min) · [A23. Censo del libro](exercises/01_auxiliary.ipynb#L01-A23) (2 min) · [A24. max() a mano](exercises/01_auxiliary.ipynb#L01-A24) (2 min) · [A28. Mejor bid y mejor ask](exercises/01_auxiliary.ipynb#L01-A28) (5 min) | Pasa de contar a buscar extremos y filtrar lados de un libro de un solo símbolo. Vuelve a [B04](exercises/01_build_exercises.ipynb#L01-B04). |
| Si ya dominas B07 y quieres reconocer por qué duplicar cálculos será incómodo. | [A27. Función nocional](exercises/01_auxiliary.ipynb#L01-A27) (5 min) · [A29. El problema que viene: dos activos](exercises/01_auxiliary.ipynb#L01-A29) (5 min) | Anticipa funciones reutilizables y separación por instrumento; L2 las enseñará de nuevo como parte obligatoria. Vuelve a [B07](exercises/01_build_exercises.ipynb#L01-B07). |
| Si el algoritmo ya está claro y quieres inspeccionar cómo lo representa el intérprete. | [8. Pregunta qué Python estás usando](exercises/01_auxiliary.ipynb#L01-B08) (2 min) · [9. Mira el bytecode real](exercises/01_auxiliary.ipynb#L01-B09) (3 min) · [A30. El alfabeto de la máquina](exercises/01_auxiliary.ipynb#L01-A30) (5 min) · [A31. Ver el bytecode con dis](exercises/01_auxiliary.ipynb#L01-A31) (5 min) | Distingue texto, código compilado y ejecución sin memorizar herramientas opcionales. Vuelve a [B07](exercises/01_build_exercises.ipynb#L01-B07). |

### De la práctica a tu proyecto

Lleva solo las fórmulas de spread y mid a student_project/exchange/snapshot.py. Comprueba allí una quote nueva; la decisión del notebook usa esos cálculos, pero no sustituye tus funciones persistentes.

**Siguiente paso:** En L2 conservaremos dato, cálculo y decisión, pero dejaremos de copiar fórmulas: una función recibirá órdenes y leerá el libro de un instrumento.

## La pieza que construyes en tu sistema

**Partes de:** Partimos de una quote de un único instrumento: bid es el precio disponible para vender y ask el precio disponible para comprar. En snapshot.py ya están nombrados bid y ask; todavía no hay funciones ni ejecución de órdenes.

**Problema:** Convertir esos dos datos en dos lecturas distintas y comprobables: cuánto separa ambos lados y dónde está su punto medio. El sistema necesita conservar los números, no solo imprimir una frase con ellos.

### Cómo lo hemos pensado

1. Lee primero bid y ask y conserva su unidad: USD por unidad del instrumento. Una resta de precios sigue siendo un precio; no es un porcentaje ni el coste total de una orden de cualquier tamaño.
2. Asigna a spread la distancia desde bid hasta ask. El orden de la resta importa: para una quote normal, el resultado es no negativo; invertir la resta cambia el significado.
3. Asigna a mid el promedio de los dos precios. Agrupa la suma antes de dividir para que ambos lados tengan el mismo peso.
4. Calcula ambos derivados después de los datos de entrada. Son variables calculadas una vez al ejecutar el archivo: cambiar bid más tarde no recalcula automáticamente spread ni mid.

**Predice y contrasta:** Con bid=99 y ask=101, la distancia es 101−99=2 USD por unidad y el promedio es (99+101)/2=100 USD por unidad. Por tanto snapshot.py debe dejar spread=2 y mid=100. Si repetimos el cálculo para bid=102 y ask=106, esperamos spread=4 y mid=104. Comprar una unidad a 101 y venderla inmediatamente a 99 perdería 2 antes de costes; el mid 100 por sí solo no es un precio garantizado de ejecución.

**Del ejemplo a tu implementación:** B01–B02 nombran una quote y calculan sus derivados; B07 los usa para razonar una decisión. El proyecto conserva exactamente ese cálculo en snapshot.py, con precios pequeños para verificarlo a mano. Sus targets spread y mid son variables asignadas, no funciones; las listas, órdenes y decisiones practicadas en el principal aportan contexto sin cambiar esta entrega.

### Construcción principal

Trabaja en `student_project/exchange/`. Los ejercicios preparan las decisiones; la entrega central es completar estos cuerpos en tus archivos. El resto del código del starter está proporcionado y se puede leer.

- **`snapshot.py:spread`** — En snapshot.py localiza bid y ask y completa spread con la distancia entre ambos. Predice su signo y valor para 99/101 antes de ejecutar; después cambia ambos datos y vuelve a ejecutar para comprobar que la fórmula depende de ellos. Preparación: [L01-B01](exercises/01_build_exercises.ipynb#L01-B01) · [L01-B02](exercises/01_build_exercises.ipynb#L01-B02).
- **`snapshot.py:mid`** — Completa mid usando ambos precios con igual peso. Comprueba que para 99/101 queda a una unidad de cada extremo y explica por qué leer mid no demuestra que puedas comprar o vender a ese precio. Preparación: [L01-B02](exercises/01_build_exercises.ipynb#L01-B02) · [L01-B07](exercises/01_build_exercises.ipynb#L01-B07).

**Comprobación acumulativa:** desde la raíz de tu carpeta de estudio, ejecuta `python check_project.py 1` después de completar tus archivos. Que pase un miniejercicio no sustituye esta integración.

**Lo siguiente reutiliza:** L2 seleccionará los mejores precios entre varias órdenes. L3 aplicará estas mismas fórmulas al par seleccionado, en vez de usar una quote fija.

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

El notebook practica tipos básicos (`int`, `float`, `str`), listas, diccionarios,
`for` e `if`. Una orden didáctica reúne `symbol`, `side`, `price` y `size` en un dict.
En el proyecto propio completas `student_project/exchange/snapshot.py`: con bid=99 y ask=101,
`spread` debe ser 2 y `mid`, 100. Estas asignaciones son una primera exploración; las funciones
de L2 reutilizan la idea, no importan literalmente este archivo.

La presentación es una explicación interactiva en JavaScript, no un kernel Python. Sus
estados ilustran ejecución, variables y decisiones. Python y Jupyter se ejecutan en local,
siguiendo `GUIA_LOCAL.md`. Explorar `ord`, `bin` o `dis` queda en OPTIONAL.
El vocabulario de las órdenes reaparece en las clases de L4.

## Ejercicios de construcción

- **1. Enciende el mercado** — variables
- **2. Spread y mid** — operaciones y tipos
- **A1. Ticks enteros** — // y % (división entera y resto)
- **A2. Redondeo decimal, no rejilla de ticks** — round
- **A3. PnL con signo** — abs y signo
- **3. Una lista de mids** — listas e indexing
- **4. Media con un bucle** — for y acumuladores
- **A13. Ventana de ticks** — slicing
- **A14. Llega un tick** — append
- **5. Una orden, y cómo leerla** — diccionarios: crear y acceder
- **A6. Base y quote** — slicing de strings
- **A7. Limpia el input** — strip / upper / endswith
- **A8. Parsea una quote** — split + int
- **A9. El ticket perfecto** — f-strings con formato
- **A18. Lee con red** — get con default
- **6. Clasifica el mercado** — if / elif / else
- **7. Tu primer algoritmo** — dato → cálculo → decisión
- **A11. ¿Puedo operar?** — and

## Estructura de la carpeta

- `presentation/` — presentación interactiva
- `exercises/01_build_exercises.ipynb` — construyes la pieza (LIVE y REQUIRED: preparación y construcción del sistema)
- `exercises/01_auxiliary.ipynb` — solo variantes y drills OPTIONAL

## Idea central

> Un algoritmo es siempre lo mismo: dato → cálculo → decisión.
