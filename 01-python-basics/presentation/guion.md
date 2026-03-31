# Guion — Clase 1: Python para Trading

La presentacion tiene 3 bloques + hero + cierre. Duracion total: 20 minutos.

## Idea central

**Python es texto que un programa lee. Los errores te dicen donde mirar. Y con variables, operaciones e `if` ya puedes tomar decisiones automaticas.**

## Como usar este guion

Cada bloque tiene:
- `Objetivo`: que debe entender el alumno.
- `Que decir`: frases clave para verbalizar.
- `Accion en pantalla`: que tocar o demostrar.
- `Riesgo`: errores de framing que evitar.
- `Salida`: la frase mental con la que deberian quedarse.

---

## Hero (2 min)

### Objetivo
Fijar el tono: hoy no memorizamos, entendemos. Y lo conectamos con trading desde el minuto uno.

### Accion en pantalla
- Senala el snapshot de mercado (bid/ask/spread/mid).
- Pulsa "Otro snapshot" para mostrar que los datos cambian.
- Senala la timeline de 3 bloques.

### Que decir
- "Hoy no quiero que memoriceis comandos. Quiero que entendais que pasa cuando escribes algo y pulsas ejecutar."
- "Vamos a trabajar siempre con datos de mercado, no con ejemplos abstractos."
- "La clase tiene tres pasos: escribir codigo, romperlo a proposito, y tomar una decision automatica."

### Riesgo
- No alargar la apertura. Maximo 2 minutos.

### Salida
- "Hay un programa real leyendo mi texto."

---

## Bloque 1: Tu codigo es texto (5 min)

### Objetivo
Que el alumno escriba Python real en el navegador y vea causa-efecto inmediato.

### Accion en pantalla
- Escribe en el editor en vivo: `bid = 99950`, `ask = 100000`, etc.
- Pulsa Ejecutar (o Ctrl+Enter). Muestra el resultado.
- Usa los botones "Variables y tipos", "Lista y for", "Diccionario" para mostrar progresion.

### Que decir
- "Esto es solo texto. Un `.py` no es un objeto misterioso."
- "Python lee ese texto, entiende la estructura, y produce un resultado."
- "Si borrases Python del ordenador, el archivo seguiria ahi pero ya no habria nadie que lo interpretara."

### Riesgo
- No entrar en detalles de tokenizacion, AST, bytecode o VM. La intuicion "texto -> interprete -> resultado" es suficiente.
- No presentar Python como magia ni como algo trivial.

### Salida
- "Python lee texto y produce resultados. Nada mas."

---

## Bloque 2: Los errores son pistas (5 min)

### Objetivo
Desmitificar los errores. Que el alumno los vea como informacion util, no como castigo.

### Accion en pantalla
- Recorre los 4 retos interactivos en orden.
- En cada uno, primero pulsa Ejecutar para ver el error.
- Deja que los alumnos intenten arreglarlo.
- Senala la pista que aparece.
- Al resolverlo, aparece el siguiente reto automaticamente.

### Que decir
- "Un error es Python diciendote exactamente donde y por que no puede continuar."
- "Hay dos grandes familias:"
  - "SyntaxError: Python no entiende la frase. Le falta algo (parentesis, comilla, dos puntos)."
  - "Runtime errors (NameError, TypeError, ZeroDivisionError): la frase esta bien escrita pero algo falla al ejecutarla."
- "La habilidad mas util de un programador no es evitar errores — es leerlos rapido."

### Riesgo
- No conviertas esto en una clase de clasificacion de errores. Son 4 ejemplos, no una taxonomia.
- No digas que `prnt("hola")` es SyntaxError — es NameError (la sintaxis es valida).

### Salida
- "Un error no es un castigo. Es Python ayudandote a encontrar el problema."

---

## Bloque 3: Del dato a la decision (7 min)

### Objetivo
Mostrar la estructura basica de cualquier algoritmo: dato -> calculo -> decision.

### Accion en pantalla
- Senala el snapshot interactivo (bid/ask/spread/mid/market_state).
- Pulsa "Cambiar mercado" varias veces para ver como cambian los valores.
- Construye una regla en el rule builder: "Si spread <= 50 -> comprar".
- Cambia el mercado y ve como la decision cambia automaticamente.
- Muestra el editor de codigo a la derecha — es el mismo algoritmo escrito en Python.
- Ejecuta el codigo.

### Que decir
- "Un algoritmo no es mas que esto: leer datos, calcular algo y decidir."
- "Aqui has pasado de un dato crudo (bid/ask) a un calculo (spread) a una clasificacion (market_state) a una decision (action)."
- "En el notebook vais a construir esto paso a paso con mas detalle."

### Riesgo
- No presentar la regla como una estrategia real. Es un toy example pedagogico.
- No entrar en funciones aqui — eso va en el notebook.

### Salida
- "Dato -> calculo -> decision. Esa es la estructura de cualquier algo."

---

## Cierre (1 min)

### Objetivo
Cerrar el mapa mental y preparar la transicion al notebook.

### Que decir
- "Ya no entramos al notebook a ciegas. Entramos sabiendo que hay un interprete, que los errores te guian, y que la estructura es siempre dato-calculo-decision."
- "Ahora toca practicar: abrid el notebook y construid vuestro primer mini sistema pieza a pieza."

### Salida
- "Ya tengo el mapa mental; ahora toca practicar."

---

## Checklist rapido

- [ ] He dejado claro que Python es un programa que lee texto.
- [ ] He diferenciado SyntaxError de errores de runtime con ejemplos concretos.
- [ ] He construido dato -> calculo -> decision en vivo.
- [ ] He conectado el final con la practica del notebook.
- [ ] No he mencionado AST, bytecode ni VM como secciones propias.
- [ ] Todo ha sido con datos de trading, no ejemplos abstractos.
