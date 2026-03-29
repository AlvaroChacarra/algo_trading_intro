# Guion de la presentacion: Libraries + OOP - Clase 2

Este guion acompana la version interactiva de la presentacion.

Regla de uso:

- La pantalla fija el mapa mental.
- Tu voz hace las conexiones y marca el ritmo.
- El notebook convierte la intuicion en codigo.

La clase esta construida alrededor de una idea central:

**Una libreria amplia tu caja de herramientas. Una clase organiza las tuyas. Un tracker convierte eventos en estado.**

## Como usar este guion

En cada bloque tienes:

- `Objetivo`: que debe quedar claro.
- `Accion en pantalla`: que conviene tocar o activar.
- `Que decir`: frases utiles para verbalizar.
- `Riesgo`: error de framing que conviene evitar.
- `Salida`: frase corta para cerrar el bloque.

## Bloque 0: Hero

Corresponde al hero y al panel `workspace vivo`.

### Objetivo

Abrir la clase con una secuencia clara: tool -> object -> state.

### Accion en pantalla

- Senala la banda `Hoy vas a hacer 3 cosas` para fijar el mapa desde el minuto uno.
- Deja que roten las tabs del hero o recorre manualmente `import`, `tabla`, `objeto`, `estado`.
- Usa el panel derecho para anticipar que la clase no se queda en teoria.

### Que decir

- "Hoy no vamos a memorizar OOP. Vamos a notar por que el codigo cambia de forma."
- "Primero traemos herramientas. Luego definimos objetos. Al final movemos estado."
- "Ese salto es el que convierte codigo suelto en piezas de sistema."

### Riesgo

- No presentar OOP como algo academico.
- No vender `pandas` como tema principal de la sesion.

### Salida

- "La clase tiene una direccion clara: tooling, structure, state."

## Bloque 1: Before / After import

Corresponde a la seccion `Mismo dataset. Muy distinta capacidad operativa.`

### Objetivo

Hacer visible que `import` no es magia; es acceso a herramientas mejores.

### Accion en pantalla

- Cambia entre `Sin libreria` y `Con pandas`.
- Para unos segundos en el snippet y en la lista `que cambia`.

### Que decir

- "El dataset es el mismo. Lo que cambia es la ergonomia."
- "Sin libreria, el trabajo existe, pero es mas artesanal."
- "Con pandas, operas sobre una estructura hecha para leer, filtrar y resumir."

### Riesgo

- No entrar en detalles internos de importacion, entornos o packaging.
- No presentar `import` como copia magica dentro del archivo.

### Salida

- "Importar es abrir acceso a una herramienta que te ahorra friccion."

## Bloque 2: Pandas live table

Corresponde a la tabla reactiva y los counters.

### Objetivo

Dar un momento de "aha": el dataset responde a decisiones concretas.

### Accion en pantalla

- Filtra `Solo buy`.
- Pulsa `Calcular notional`.
- Pulsa `Agrupar por side`.
- Senala como cambian tabla, metricas, resumen lateral y panel `lectura guiada`.

### Que decir

- "Aqui no estamos estudiando pandas en profundidad."
- "Solo queremos sentir el salto: la tabla ya no es texto, es una superficie operable."
- "En pocos gestos ya filtras, calculas y resumes."

### Riesgo

- No alargar esta parte demasiado.
- No dejar que el alumno piense que la clase 2 es una mini clase de data analysis.

### Salida

- "Una libreria buena comprime mucho trabajo mental."

## Bloque 3: Dict -> Class -> Object

Corresponde al diagrama y al panel de foco `dict / class / object`.

### Objetivo

Explicar por que el dict fue correcto en lesson 1 y por que ahora empieza a quedarse corto.

### Accion en pantalla

- Recorre las tabs `dict`, `class`, `object`.
- Usa el SVG como puente visual entre lesson 1 y lesson 2.

### Que decir

- "Un dict guarda datos rapido. Para empezar era la decision correcta."
- "El problema aparece cuando formulas y descripciones empiezan a repetirse."
- "La clase fija una forma reusable; el objeto es una instancia concreta de esa forma."

### Riesgo

- No vender la clase como sustituto obligatorio de cualquier dict.
- No abrir temas como herencia o polimorfismo.

### Salida

- "La clase no complica. Ordena."

## Bloque 4: Order playground + tracker

Corresponde al playground principal.

### Objetivo

Unir las dos mitades de la clase: construir un objeto y ver como sus eventos mueven estado.

### Accion en pantalla

- Cambia `price`, `size` o `mark price`.
- Pulsa `Crear order`.
- Pulsa `Compra demo`.
- Pulsa `Venta parcial` o `Secuencia completa`.
- Ensena el cambio en `cash`, `position`, `equity`, el panel de consecuencia y el log.

### Que decir

- "Aqui la clase deja de ser definicion y se convierte en pieza de trabajo."
- "Order organiza datos y comportamiento."
- "Trade representa un evento."
- "PositionTracker acumula consecuencias y convierte eventos en estado."

### Riesgo

- No atascarse en sintaxis fina de `self`.
- No vender el tracker como motor de trading real; es un mini sistema pedagogico.

### Salida

- "Cuando aparece estado, el codigo empieza a parecerse a un sistema."

## Bloque 5: Cierre

Corresponde al pipeline mental del final.

### Objetivo

Cerrar la clase con una secuencia memorable y preparar el notebook.

### Accion en pantalla

- Recorre la timeline `Import -> Tabla -> Order -> Trade -> Estado`.
- Vuelve al playground si quieres cerrar con un ejemplo concreto.

### Que decir

- "No has aprendido toda OOP. Has aprendido por que aparece."
- "Primero amplias capacidad con herramientas externas."
- "Luego haces que tu propio codigo tambien se comporte como herramienta reusable."

### Riesgo

- No cerrar con vocabulario tecnico de mas.
- No dejar la sensacion de que lesson 1 queda invalidada.

### Salida

- "Tool -> data -> object -> event -> state."

## Transicion al notebook

Frase recomendada para abrir el notebook:

**"En la presentacion hemos fijado el mapa mental. Ahora vamos a escribir el camino: import, tabla, Order, Trade y un tracker pequeno."**

## Recordatorios del tono docente

- Mantener la continuidad con lesson 1.
- Repetir que el dict no estaba mal; simplemente ahora necesitamos una estructura mejor.
- Tratar `pandas` como herramienta puntual, no como protagonista.
- Tratar OOP como una forma de organizar codigo con sentido, no como teoria abstracta.
